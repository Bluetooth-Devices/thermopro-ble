"""
TP902 (TP920) BLE protocol support.

The TP902 / TP920 multi-probe meat thermometer does not broadcast sensor data
in BLE advertisements. Instead, a host must connect over GATT, send an auth
handshake, subscribe to the notify characteristic, and decode framed packets.

Protocol reference and packet captures originally documented in
https://github.com/petrkr/thermopro-tp902 (MIT License).

This module is experimental: encode/decode helpers are unit-tested against
known captures, but the GATT-side ``TP902Device`` is unverified against real
hardware and may need adjustment once captures from production devices are
available.

Packet frame: ``CMD LEN DATA[LEN] CHECKSUM`` where
``CHECKSUM = sum(frame[0:2 + LEN]) & 0xFF``. Temperatures are encoded as
2-byte BCD in tenths of a degree; ``0xFFFF`` means the probe slot is empty.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

_LOGGER = logging.getLogger(__name__)


TP902_SERVICE_UUID = UUID("1086fff0-3343-4817-8bb2-b32206336ce8")
TP902_WRITE_UUID = UUID("1086fff1-3343-4817-8bb2-b32206336ce8")
TP902_NOTIFY_UUID = UUID("1086fff2-3343-4817-8bb2-b32206336ce8")

# TX command codes
CMD_AUTH = 0x01
CMD_BACKLIGHT_ON = 0x02
CMD_SET_UNITS = 0x20
CMD_SET_SOUND = 0x21
CMD_SET_ALARM = 0x23
CMD_GET_ALARM = 0x24
CMD_GET_STATUS = 0x26
CMD_SNOOZE_ALARM = 0x27
CMD_TIME_SYNC = 0x28
CMD_GET_FW = 0x41

# RX command codes
RX_AUTH = 0x01
RX_ALARM = 0x24
RX_TEMP_ACTUAL = 0x25
RX_STATUS = 0x26
RX_TEMP_BROADCAST = 0x30
RX_FW_VERSION = 0x41
RX_ERROR = 0xE0

# Value byte constants used both ways on the wire
UNITS_C = 0x0C
UNITS_F = 0x0F
SOUND_ON = 0x0C
SOUND_OFF = 0x0F

# Alarm modes used in 0x23 / 0x24 commands
ALARM_OFF = 0x00
ALARM_TARGET = 0x0A
ALARM_RANGE = 0x82

PROBE_COUNT = 6
_PROBE_EMPTY = b"\xff\xff"

# Fixed auth handshake captured from the official mobile app. The handshake
# uses a randomized payload in the wild; this deterministic value is what
# petrkr/thermopro-tp902 observed the device accepting.
AUTH_PACKET = bytes.fromhex("01098a7a13b73ed68b67c2a0")

# Seconds between 1970-01-01 and 2020-01-01 UTC. The device's clock counts
# from the latter epoch.
EPOCH_2020 = 1_577_836_800


def _units_byte_to_str(raw: int) -> str:
    if raw == UNITS_C:
        return "C"
    if raw == UNITS_F:
        return "F"
    return f"0x{raw:02x}"


def decode_temp_bcd(raw: bytes) -> float | None:
    """Decode a 2-byte BCD temperature in tenths of a degree.

    Returns ``None`` for the empty-probe sentinel ``0xFFFF``. The high bit of
    the first byte is used as a sign flag.
    """
    if len(raw) != 2:
        raise ValueError(f"expected 2 bytes, got {len(raw)}")
    if raw == _PROBE_EMPTY:
        return None
    neg = bool(raw[0] & 0x80)
    b0 = raw[0] & 0x7F
    b1 = raw[1]
    hundreds = (b0 >> 4) * 100
    tens = (b0 & 0x0F) * 10
    ones = b1 >> 4
    tenths = b1 & 0x0F
    value = (hundreds + tens + ones) + tenths / 10.0
    return -value if neg else value


def encode_temp_bcd(value: float | None) -> bytes:
    """Encode a temperature (tenths of a degree) as 2 BCD bytes.

    ``None`` yields the empty-probe sentinel ``0xFFFF``. Values outside the
    range ``-999.9 .. 999.9`` raise ``ValueError``.
    """
    if value is None:
        return _PROBE_EMPTY
    if not -999.9 <= value <= 999.9:
        raise ValueError(f"temperature out of BCD range: {value}")
    neg = value < 0
    tenths_total = int(round(abs(value) * 10))
    ones_total, tenths = divmod(tenths_total, 10)
    ones = ones_total % 10
    tens = (ones_total // 10) % 10
    hundreds = (ones_total // 100) % 10
    b0 = (hundreds << 4) | tens
    b1 = (ones << 4) | tenths
    if neg:
        b0 |= 0x80
    return bytes([b0, b1])


def build_packet(cmd: int, payload: bytes = b"") -> bytes:
    """Build a TP902 packet frame: ``CMD LEN DATA CHECKSUM``."""
    if not 0 <= cmd <= 0xFF:
        raise ValueError(f"cmd out of range: {cmd}")
    if len(payload) > 0xFF:
        raise ValueError(f"payload too long: {len(payload)}")
    header = bytes([cmd, len(payload)])
    checksum = (sum(header) + sum(payload)) & 0xFF
    return header + payload + bytes([checksum])


def verify_checksum(data: bytes) -> bool:
    """Return True when ``data`` carries a valid TP902 frame checksum."""
    if len(data) < 3:
        return False
    pkt_len = data[1]
    if len(data) < 2 + pkt_len + 1:
        return False
    end = 2 + pkt_len
    expected = sum(data[:end]) & 0xFF
    return expected == data[end]


@dataclass(frozen=True)
class TemperatureBroadcast:
    """Periodic temperature broadcast (RX cmd 0x30).

    ``temperatures`` is a tuple of ``PROBE_COUNT`` floats (in the unit the
    device is configured to display) or ``None`` when the probe slot is
    empty.
    """

    battery: int
    units: str
    alarms: int
    temperatures: tuple[float | None, ...]


@dataclass(frozen=True)
class TemperatureSnapshot:
    """One-shot temperature snapshot (RX cmd 0x25)."""

    probe_count: int
    alarms: int
    temperatures: tuple[float | None, ...]


@dataclass(frozen=True)
class DeviceStatus:
    """Device status / config (RX cmd 0x26)."""

    units: str
    beeper_on: bool
    battery: int


@dataclass(frozen=True)
class AlarmConfig:
    """Per-channel alarm configuration (RX cmd 0x24)."""

    channel: int
    mode: int
    value1: float | None
    value2: float | None


@dataclass(frozen=True)
class FirmwareVersion:
    """Firmware version (RX cmd 0x41)."""

    major: int
    minor: int


@dataclass(frozen=True)
class AuthResponse:
    """Auth handshake response (RX cmd 0x01)."""

    data: bytes


@dataclass(frozen=True)
class UnknownFrame:
    """Frame whose layout is not yet decoded."""

    cmd: int
    data: bytes


Notification = (
    TemperatureBroadcast
    | TemperatureSnapshot
    | DeviceStatus
    | AlarmConfig
    | FirmwareVersion
    | AuthResponse
    | UnknownFrame
)


def _decode_probe_temps(data: bytes, offset: int) -> tuple[float | None, ...]:
    """Decode ``PROBE_COUNT`` BCD temperature pairs starting at ``offset``."""
    out: list[float | None] = []
    for i in range(PROBE_COUNT):
        start = offset + i * 2
        end = start + 2
        out.append(decode_temp_bcd(data[start:end]))
    return tuple(out)


def parse_notification(raw: bytes) -> Notification | None:
    """Parse a single TP902 notification frame.

    Returns ``None`` when the frame is too short to contain ``CMD LEN`` or
    when the checksum does not verify. Otherwise returns the decoded
    dataclass, falling back to :class:`UnknownFrame` for command codes whose
    layout is not yet implemented here.
    """
    if len(raw) < 3 or not verify_checksum(raw):
        return None

    cmd = raw[0]
    pkt_len = raw[1]
    data_end = 2 + pkt_len
    data = raw[2:data_end]

    if cmd == RX_TEMP_BROADCAST and pkt_len >= 15:
        battery = data[0]
        units = _units_byte_to_str(data[1])
        alarms = data[2]
        temps = _decode_probe_temps(data, offset=3)
        return TemperatureBroadcast(battery, units, alarms, temps)

    if cmd == RX_TEMP_ACTUAL and pkt_len >= 14:
        probe_count = data[0]
        alarms = data[1]
        temps = _decode_probe_temps(data, offset=2)
        return TemperatureSnapshot(probe_count, alarms, temps)

    if cmd == RX_STATUS and pkt_len >= 3:
        return DeviceStatus(
            units=_units_byte_to_str(data[0]),
            beeper_on=data[1] == SOUND_ON,
            battery=data[2],
        )

    if cmd == RX_ALARM and pkt_len >= 6:
        return AlarmConfig(
            channel=data[0],
            mode=data[1],
            value1=decode_temp_bcd(data[2:4]),
            value2=decode_temp_bcd(data[4:6]),
        )

    if cmd == RX_FW_VERSION and pkt_len >= 1:
        # BCD-packed X.Y in one byte (e.g. 0x12 → 1.2).
        bcd = data[0]
        return FirmwareVersion(major=bcd >> 4, minor=bcd & 0x0F)

    if cmd == RX_AUTH:
        return AuthResponse(data=bytes(data))

    return UnknownFrame(cmd=cmd, data=bytes(data))


def build_auth_packet() -> bytes:
    """Return the auth handshake frame to send first after connecting."""
    return AUTH_PACKET


def build_set_units(celsius: bool) -> bytes:
    return build_packet(CMD_SET_UNITS, bytes([UNITS_C if celsius else UNITS_F]))


def build_set_sound(enabled: bool) -> bytes:
    return build_packet(CMD_SET_SOUND, bytes([SOUND_ON if enabled else SOUND_OFF]))


def build_get_alarm(channel: int) -> bytes:
    if not 1 <= channel <= PROBE_COUNT:
        raise ValueError(f"channel must be 1..{PROBE_COUNT}, got {channel}")
    return build_packet(CMD_GET_ALARM, bytes([channel]))


def build_set_alarm(
    channel: int,
    mode: int = ALARM_OFF,
    value1: float | None = None,
    value2: float | None = None,
) -> bytes:
    """Build a set-alarm frame for the given probe channel.

    For ``ALARM_TARGET`` only ``value1`` is used; for ``ALARM_RANGE`` both
    values are required. ``ALARM_OFF`` ignores values.
    """
    if not 1 <= channel <= PROBE_COUNT:
        raise ValueError(f"channel must be 1..{PROBE_COUNT}, got {channel}")
    if mode == ALARM_OFF:
        t1, t2 = _PROBE_EMPTY, _PROBE_EMPTY
    elif mode == ALARM_TARGET:
        if value1 is None:
            raise ValueError("ALARM_TARGET requires value1")
        t1 = encode_temp_bcd(value1)
        t2 = b"\x00\x00"
    elif mode == ALARM_RANGE:
        if value1 is None or value2 is None:
            raise ValueError("ALARM_RANGE requires value1 and value2")
        t1 = encode_temp_bcd(value1)
        t2 = encode_temp_bcd(value2)
    else:
        raise ValueError(f"unknown alarm mode: 0x{mode:02x}")
    return build_packet(CMD_SET_ALARM, bytes([channel, mode]) + t1 + t2)


def build_time_sync(epoch_2020_seconds: int) -> bytes:
    """Build a time-sync frame. ``epoch_2020_seconds`` is seconds since
    2020-01-01 UTC; negative values raise ``ValueError``."""
    if epoch_2020_seconds < 0:
        raise ValueError("epoch_2020_seconds must be non-negative")
    if epoch_2020_seconds >= 1 << 32:
        raise ValueError("epoch_2020_seconds out of 32-bit range")
    return build_packet(CMD_TIME_SYNC, epoch_2020_seconds.to_bytes(4, "little"))


def supports(model_or_name: str) -> bool:
    """Return ``True`` if the device model name maps to a TP902-family probe."""
    model = model_or_name.split(" ", 1)[0]
    return model in {"TP902", "TP920"}


class TP902Device:
    """Active GATT client for a TP902 / TP920 multi-probe thermometer.

    Workflow::

        device = TP902Device(ble_device)
        async with device.session() as session:
            await session.authenticate()
            async for event in session.events():
                ...

    The session opens a connection via
    :func:`bleak_retry_connector.establish_connection`, subscribes to the
    notify characteristic, and decodes each notification through
    :func:`parse_notification`. Closing the session disconnects.

    .. warning::
       This class has been validated against documented packet captures only.
       Behaviour against real hardware may diverge — open an issue if you hit
       a mismatch.
    """

    def __init__(self, ble_device: BLEDevice) -> None:
        self.ble_device = ble_device

    def session(self) -> "TP902Session":
        """Return an unstarted session. Use as ``async with``."""
        return TP902Session(self.ble_device)


class TP902Session:
    """Active TP902 GATT session. Use via ``async with TP902Device.session()``."""

    def __init__(self, ble_device: BLEDevice) -> None:
        self._ble_device = ble_device
        self._client: BleakClient | None = None
        self._queue: asyncio.Queue[Notification] = asyncio.Queue()

    async def __aenter__(self) -> "TP902Session":  # pragma: no cover - GATT path
        self._client = await establish_connection(
            BleakClient, self._ble_device, self._ble_device.address
        )
        await self._client.start_notify(TP902_NOTIFY_UUID, self._on_notify)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:  # pragma: no cover
        client = self._client
        self._client = None
        if client is not None:
            try:
                await client.stop_notify(TP902_NOTIFY_UUID)
            except Exception:  # noqa: BLE001
                _LOGGER.debug("stop_notify failed", exc_info=True)
            await client.disconnect()

    def _on_notify(self, _sender: object, data: bytearray) -> None:
        parsed = parse_notification(bytes(data))
        if parsed is None:
            _LOGGER.debug("TP902 dropped malformed frame: %s", bytes(data).hex())
            return
        self._queue.put_nowait(parsed)

    async def _write(self, frame: bytes) -> None:  # pragma: no cover - GATT path
        if self._client is None:
            raise RuntimeError("session not started")
        await self._client.write_gatt_char(TP902_WRITE_UUID, frame, True)

    async def authenticate(self) -> None:  # pragma: no cover - GATT path
        await self._write(build_auth_packet())

    async def request_status(self) -> None:  # pragma: no cover - GATT path
        await self._write(build_packet(CMD_GET_STATUS))

    async def request_firmware(self) -> None:  # pragma: no cover - GATT path
        await self._write(build_packet(CMD_GET_FW))

    async def set_units(self, celsius: bool) -> None:  # pragma: no cover - GATT path
        await self._write(build_set_units(celsius))

    async def set_sound(self, enabled: bool) -> None:  # pragma: no cover - GATT path
        await self._write(build_set_sound(enabled))

    async def events(
        self,
        *,
        on_unknown: Callable[[UnknownFrame], None] | None = None,
    ) -> "asyncio.Queue[Notification]":  # pragma: no cover - GATT path
        """Return the queue of decoded notifications.

        ``on_unknown`` is invoked synchronously for :class:`UnknownFrame`
        items as they are dequeued by the caller — provide it as a debug
        hook when investigating new command codes.
        """
        if on_unknown is None:
            return self._queue
        # Wrap the queue so unknown frames are tee'd through the hook.
        wrapped: asyncio.Queue[Notification] = asyncio.Queue()

        async def _pump() -> None:
            while True:
                item = await self._queue.get()
                if isinstance(item, UnknownFrame):
                    on_unknown(item)
                await wrapped.put(item)

        asyncio.create_task(_pump())
        return wrapped

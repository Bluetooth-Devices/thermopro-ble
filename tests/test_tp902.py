"""Tests for the TP902 / TP920 protocol helpers."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from bleak.exc import BleakCharacteristicNotFoundError, BleakError

from thermopro_ble.tp902 import (
    ALARM_OFF,
    ALARM_RANGE,
    ALARM_TARGET,
    AUTH_PACKET,
    CMD_GET_ALARM,
    CMD_SET_ALARM,
    CMD_SET_SOUND,
    CMD_SET_UNITS,
    CMD_TIME_SYNC,
    PROBE_COUNT,
    SOUND_OFF,
    SOUND_ON,
    TP902_NOTIFY_UUID,
    TP902_WRITE_UUID,
    UNITS_C,
    UNITS_F,
    AlarmConfig,
    AuthResponse,
    DeviceStatus,
    FirmwareVersion,
    TP902Device,
    TP902Session,
    TemperatureBroadcast,
    TemperatureSnapshot,
    UnknownFrame,
    build_auth_packet,
    build_get_alarm,
    build_packet,
    build_set_alarm,
    build_set_sound,
    build_set_units,
    build_time_sync,
    decode_temp_bcd,
    encode_temp_bcd,
    parse_notification,
    supports,
    verify_checksum,
)


class TestBcd:
    def test_decode_positive(self):
        # 0x0999 → 99.9 °C (captured TP902 broadcast probe 1)
        assert decode_temp_bcd(b"\x09\x99") == 99.9

    def test_decode_three_digits(self):
        # 0x1007 → 100.7 °C (captured TP902 broadcast probe 2)
        assert decode_temp_bcd(b"\x10\x07") == 100.7

    def test_decode_empty_probe(self):
        assert decode_temp_bcd(b"\xff\xff") is None

    def test_decode_negative(self):
        # High bit of byte 0 means negative; remaining nibbles decode normally.
        assert decode_temp_bcd(b"\x82\x55") == pytest.approx(-25.5)

    def test_decode_zero(self):
        assert decode_temp_bcd(b"\x00\x00") == 0.0

    def test_decode_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            decode_temp_bcd(b"\x09")

    @pytest.mark.parametrize(
        "value,expected",
        [
            (99.9, b"\x09\x99"),
            (100.7, b"\x10\x07"),
            (0.0, b"\x00\x00"),
            (25.5, b"\x02\x55"),
        ],
    )
    def test_encode_round_trip(self, value, expected):
        assert encode_temp_bcd(value) == expected
        assert decode_temp_bcd(expected) == pytest.approx(value)

    def test_encode_negative(self):
        encoded = encode_temp_bcd(-25.5)
        assert encoded == b"\x82\x55"
        assert decode_temp_bcd(encoded) == pytest.approx(-25.5)

    def test_encode_none_yields_empty_probe(self):
        assert encode_temp_bcd(None) == b"\xff\xff"

    def test_encode_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            encode_temp_bcd(1000.0)
        with pytest.raises(ValueError):
            encode_temp_bcd(-1000.0)


class TestPacket:
    def test_build_basic_frame(self):
        # cmd=0x24 len=1 data=01 → checksum = (0x24+0x01+0x01)&0xff = 0x26
        assert build_packet(0x24, b"\x01") == b"\x24\x01\x01\x26"

    def test_build_empty_payload(self):
        # cmd=0x26 len=0 → checksum = 0x26
        assert build_packet(0x26) == b"\x26\x00\x26"

    def test_build_rejects_invalid_cmd(self):
        with pytest.raises(ValueError):
            build_packet(0x100)
        with pytest.raises(ValueError):
            build_packet(-1)

    def test_build_rejects_oversized_payload(self):
        with pytest.raises(ValueError):
            build_packet(0x24, b"\x00" * 256)

    def test_verify_checksum_round_trip(self):
        frame = build_packet(0x24, b"\x01")
        assert verify_checksum(frame) is True

    def test_verify_checksum_rejects_truncated(self):
        assert verify_checksum(b"\x24") is False
        assert verify_checksum(b"\x24\x01") is False  # missing data + cs

    def test_verify_checksum_rejects_bad_checksum(self):
        assert verify_checksum(b"\x24\x01\x01\x00") is False

    def test_verify_checksum_tolerates_padding(self):
        # Notifications are typically 20 bytes; bytes past the checksum are
        # padding and must not affect verification.
        frame = build_packet(0x24, b"\x01") + b"\x00" * 10
        assert verify_checksum(frame) is True


class TestParseNotification:
    def test_temperature_broadcast(self):
        # Captured TP902 broadcast (from issue #152):
        # cmd=0x30 len=0x0f bat=0x4c units=C alarms=0
        # probes: 99.9 / 100.7 / -- / -- / -- / --
        # checksum 0x48 then 0x01 0x20 padding.
        raw = bytes.fromhex("300f4c0c0009991007ffffffffffffffff480120")
        parsed = parse_notification(raw)
        assert isinstance(parsed, TemperatureBroadcast)
        assert parsed.battery == 0x4C  # 76 %
        assert parsed.units == "C"
        assert parsed.alarms == 0
        assert parsed.temperatures == (99.9, 100.7, None, None, None, None)
        assert len(parsed.temperatures) == PROBE_COUNT

    def test_temperature_broadcast_fahrenheit(self):
        # Same shape, units byte flipped to 0x0f.
        payload = bytes([0x4C, UNITS_F, 0x00]) + b"\x09\x99" + b"\xff\xff" * 5
        frame = build_packet(0x30, payload)
        parsed = parse_notification(frame)
        assert isinstance(parsed, TemperatureBroadcast)
        assert parsed.units == "F"
        assert parsed.temperatures[0] == 99.9

    def test_device_status(self):
        # 0x26 status: units=C, beeper ON, battery=80
        frame = build_packet(0x26, bytes([UNITS_C, SOUND_ON, 80, 0x00, 0x00]))
        parsed = parse_notification(frame)
        assert isinstance(parsed, DeviceStatus)
        assert parsed.units == "C"
        assert parsed.beeper_on is True
        assert parsed.battery == 80

    def test_device_status_beeper_off(self):
        frame = build_packet(0x26, bytes([UNITS_F, SOUND_OFF, 42, 0x00, 0x00]))
        parsed = parse_notification(frame)
        assert isinstance(parsed, DeviceStatus)
        assert parsed.units == "F"
        assert parsed.beeper_on is False
        assert parsed.battery == 42

    def test_alarm_range(self):
        # Issue #152 capture: ch1 RANGE lo=80.9°C hi=119.7°C
        raw = bytes.fromhex("2406018211970809660000000000510f0400392e")
        parsed = parse_notification(raw)
        assert isinstance(parsed, AlarmConfig)
        assert parsed.channel == 1
        assert parsed.mode == ALARM_RANGE
        # value1 = 119.7 (hi), value2 = 80.9 (lo); both BCD-encoded.
        assert parsed.value1 == pytest.approx(119.7)
        assert parsed.value2 == pytest.approx(80.9)

    def test_alarm_target(self):
        # Issue #152 capture: ch2 TARGET=74.0°C
        raw = bytes.fromhex("2406020a074000007d0000000000510f0400be3a")
        parsed = parse_notification(raw)
        assert isinstance(parsed, AlarmConfig)
        assert parsed.channel == 2
        assert parsed.mode == ALARM_TARGET
        assert parsed.value1 == pytest.approx(74.0)

    def test_firmware_version(self):
        frame = build_packet(0x41, bytes([0x12]))
        parsed = parse_notification(frame)
        assert isinstance(parsed, FirmwareVersion)
        assert parsed.major == 1
        assert parsed.minor == 2

    def test_auth_response(self):
        frame = build_packet(0x01, b"\xab\xcd")
        parsed = parse_notification(frame)
        assert isinstance(parsed, AuthResponse)
        assert parsed.data == b"\xab\xcd"

    def test_temperature_snapshot(self):
        # 0x25 snapshot: probe_count=6, alarms=0, all probes at 50.0°C
        body = bytes([6, 0]) + encode_temp_bcd(50.0) * PROBE_COUNT
        frame = build_packet(0x25, body)
        parsed = parse_notification(frame)
        assert isinstance(parsed, TemperatureSnapshot)
        assert parsed.probe_count == 6
        assert parsed.temperatures == (50.0,) * PROBE_COUNT

    def test_unknown_cmd_is_preserved(self):
        frame = build_packet(0x7E, b"\xde\xad\xbe\xef")
        parsed = parse_notification(frame)
        assert isinstance(parsed, UnknownFrame)
        assert parsed.cmd == 0x7E
        assert parsed.data == b"\xde\xad\xbe\xef"

    def test_too_short(self):
        assert parse_notification(b"\x30") is None

    def test_bad_checksum(self):
        # Build a valid frame, then flip the checksum byte.
        frame = bytearray(build_packet(0x26))
        frame[-1] ^= 0xFF
        assert parse_notification(bytes(frame)) is None


class TestBuilders:
    def test_auth_packet_constant(self):
        # Auth handshake is a fixed captured payload.
        assert build_auth_packet() == AUTH_PACKET
        assert len(AUTH_PACKET) == 12

    def test_set_units_celsius(self):
        frame = build_set_units(celsius=True)
        assert frame[0] == CMD_SET_UNITS
        assert frame[2] == UNITS_C
        assert verify_checksum(frame)

    def test_set_units_fahrenheit(self):
        frame = build_set_units(celsius=False)
        assert frame[2] == UNITS_F

    def test_set_sound(self):
        on = build_set_sound(True)
        off = build_set_sound(False)
        assert on[0] == CMD_SET_SOUND and on[2] == SOUND_ON
        assert off[2] == SOUND_OFF

    def test_get_alarm_channel_validation(self):
        assert build_get_alarm(1)[0] == CMD_GET_ALARM
        with pytest.raises(ValueError):
            build_get_alarm(0)
        with pytest.raises(ValueError):
            build_get_alarm(PROBE_COUNT + 1)

    def test_set_alarm_off(self):
        frame = build_set_alarm(1, ALARM_OFF)
        assert frame[0] == CMD_SET_ALARM
        # body: channel, mode, ff ff 00 00? - actually for OFF both are ff ff
        body = frame[2:-1]
        assert body[0] == 1
        assert body[1] == ALARM_OFF
        assert body[2:] == b"\xff\xff\xff\xff"

    def test_set_alarm_target_requires_value(self):
        with pytest.raises(ValueError):
            build_set_alarm(1, ALARM_TARGET)

    def test_set_alarm_target(self):
        frame = build_set_alarm(2, ALARM_TARGET, value1=74.0)
        body = frame[2:-1]
        assert body[0] == 2
        assert body[1] == ALARM_TARGET
        assert decode_temp_bcd(body[2:4]) == pytest.approx(74.0)
        assert body[4:] == b"\x00\x00"

    def test_set_alarm_range(self):
        frame = build_set_alarm(1, ALARM_RANGE, value1=119.7, value2=80.9)
        body = frame[2:-1]
        assert body[0] == 1
        assert body[1] == ALARM_RANGE
        assert decode_temp_bcd(body[2:4]) == pytest.approx(119.7)
        assert decode_temp_bcd(body[4:6]) == pytest.approx(80.9)

    def test_set_alarm_range_requires_both_values(self):
        with pytest.raises(ValueError):
            build_set_alarm(1, ALARM_RANGE, value1=119.7)
        with pytest.raises(ValueError):
            build_set_alarm(1, ALARM_RANGE, value2=80.9)

    def test_set_alarm_rejects_unknown_mode(self):
        with pytest.raises(ValueError):
            build_set_alarm(1, 0x77)

    def test_set_alarm_rejects_bad_channel(self):
        with pytest.raises(ValueError):
            build_set_alarm(0, ALARM_OFF)
        with pytest.raises(ValueError):
            build_set_alarm(PROBE_COUNT + 1, ALARM_OFF)

    def test_time_sync(self):
        frame = build_time_sync(0)
        assert frame[0] == CMD_TIME_SYNC
        # 4-byte LE payload
        assert frame[2:6] == b"\x00\x00\x00\x00"
        assert verify_checksum(frame)

    def test_time_sync_range(self):
        with pytest.raises(ValueError):
            build_time_sync(-1)
        with pytest.raises(ValueError):
            build_time_sync(1 << 32)


class TestSupports:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("TP902", True),
            ("TP920", True),
            ("TP902 (2142)", True),
            ("TP920 (abc)", True),
            ("TP357", False),
            ("TP358S", False),
            ("", False),
            ("TP9", False),
        ],
    )
    def test_supports(self, name, expected):
        assert supports(name) is expected


def _make_ble_device(
    name: str = "TP902 (1234)", address: str = "AA:BB:CC:DD:EE:FF"
) -> Any:
    ble = MagicMock()
    ble.name = name
    ble.address = address
    return ble


def _make_client(
    *,
    notify_raises: BaseException | None = None,
    stop_notify_raises: BaseException | None = None,
) -> MagicMock:
    """Build a fake BleakClientWithServiceCache with the methods we touch."""
    client = MagicMock()
    client.start_notify = AsyncMock(side_effect=notify_raises)
    client.stop_notify = AsyncMock(side_effect=stop_notify_raises)
    client.write_gatt_char = AsyncMock()
    client.disconnect = AsyncMock()
    client.clear_cache = AsyncMock()
    return client


class TestTP902DeviceWiring:
    def test_session_is_unstarted(self) -> None:
        device = TP902Device(_make_ble_device(), connector=AsyncMock())
        session = device.session()
        assert isinstance(session, TP902Session)
        assert session._client is None  # type: ignore[attr-defined]

    def test_device_default_connector(self) -> None:
        # No connector argument → default factory wired
        device = TP902Device(_make_ble_device())
        assert device._connector is not None  # type: ignore[attr-defined]


@pytest.mark.asyncio
class TestTP902SessionLifecycle:
    async def test_enter_starts_notify_on_correct_uuid(self) -> None:
        client = _make_client()
        connector = AsyncMock(return_value=client)
        session = TP902Session(_make_ble_device(), connector=connector)

        async with session:
            connector.assert_awaited_once()
            client.start_notify.assert_awaited_once()
            uuid_arg = client.start_notify.await_args.args[0]
            assert uuid_arg == TP902_NOTIFY_UUID

        client.stop_notify.assert_awaited_once()
        client.disconnect.assert_awaited_once()

    async def test_exit_swallows_bleak_error_from_stop_notify(self) -> None:
        client = _make_client(stop_notify_raises=BleakError("not connected"))
        session = TP902Session(
            _make_ble_device(), connector=AsyncMock(return_value=client)
        )
        async with session:
            pass
        # disconnect still runs even though stop_notify raised
        client.disconnect.assert_awaited_once()

    async def test_exit_without_enter_is_noop(self) -> None:
        session = TP902Session(_make_ble_device(), connector=AsyncMock())
        await session.__aexit__(None, None, None)  # no client to clean up

    async def test_retries_when_characteristic_not_found(self) -> None:
        first = _make_client(notify_raises=BleakCharacteristicNotFoundError("notify"))
        second = _make_client()
        connector = AsyncMock(side_effect=[first, second])
        session = TP902Session(_make_ble_device(), connector=connector)

        async with session:
            assert connector.await_count == 2
            first.clear_cache.assert_awaited_once()
            first.disconnect.assert_awaited_once()
            second.start_notify.assert_awaited_once()

    async def test_retries_on_generic_bleak_error(self) -> None:
        first = _make_client(notify_raises=BleakError("boom"))
        second = _make_client()
        connector = AsyncMock(side_effect=[first, second])
        session = TP902Session(_make_ble_device(), connector=connector)

        async with session:
            assert connector.await_count == 2
            # generic BleakError path should NOT clear cache
            first.clear_cache.assert_not_called()
            first.disconnect.assert_awaited_once()

    async def test_second_attempt_failure_propagates(self) -> None:
        first = _make_client(notify_raises=BleakError("boom"))
        second = _make_client(notify_raises=BleakError("still bad"))
        connector = AsyncMock(side_effect=[first, second])
        session = TP902Session(_make_ble_device(), connector=connector)

        with pytest.raises(BleakError):
            await session.__aenter__()

        assert connector.await_count == 2

    async def test_clear_cache_failure_does_not_block_retry(self) -> None:
        first = _make_client(notify_raises=BleakCharacteristicNotFoundError("notify"))
        first.clear_cache = AsyncMock(side_effect=BleakError("cache fail"))
        second = _make_client()
        connector = AsyncMock(side_effect=[first, second])
        session = TP902Session(_make_ble_device(), connector=connector)

        async with session:
            # despite clear_cache raising, the second attempt still happens
            assert connector.await_count == 2


@pytest.mark.asyncio
class TestTP902SessionWrites:
    async def _open(self) -> tuple[TP902Session, MagicMock]:
        client = _make_client()
        session = TP902Session(
            _make_ble_device(), connector=AsyncMock(return_value=client)
        )
        await session.__aenter__()
        return session, client

    async def test_write_requires_open_session(self) -> None:
        session = TP902Session(_make_ble_device(), connector=AsyncMock())
        with pytest.raises(RuntimeError, match="not started"):
            await session._write(b"\x00\x00\x00")  # type: ignore[attr-defined]

    async def test_authenticate_writes_auth_packet(self) -> None:
        session, client = await self._open()
        try:
            await session.authenticate()
        finally:
            await session.__aexit__(None, None, None)

        client.write_gatt_char.assert_awaited_once()
        uuid_arg, frame_arg, response_arg = client.write_gatt_char.await_args.args
        assert uuid_arg == TP902_WRITE_UUID
        assert frame_arg == AUTH_PACKET
        assert response_arg is True

    async def test_request_status_writes_get_status_frame(self) -> None:
        session, client = await self._open()
        try:
            await session.request_status()
        finally:
            await session.__aexit__(None, None, None)

        frame = client.write_gatt_char.await_args.args[1]
        # CMD_GET_STATUS = 0x26, len = 0, checksum = 0x26
        assert frame == bytes([0x26, 0x00, 0x26])

    async def test_request_firmware_writes_get_fw_frame(self) -> None:
        session, client = await self._open()
        try:
            await session.request_firmware()
        finally:
            await session.__aexit__(None, None, None)

        frame = client.write_gatt_char.await_args.args[1]
        # CMD_GET_FW = 0x41, len = 0, checksum = 0x41
        assert frame == bytes([0x41, 0x00, 0x41])

    async def test_set_units_celsius_and_fahrenheit(self) -> None:
        session, client = await self._open()
        try:
            await session.set_units(True)
            await session.set_units(False)
        finally:
            await session.__aexit__(None, None, None)

        frames = [c.args[1] for c in client.write_gatt_char.await_args_list]
        # CMD_SET_UNITS = 0x20; payload[0] = UNITS_C / UNITS_F
        assert frames[0] == bytes([0x20, 0x01, UNITS_C, (0x20 + 0x01 + UNITS_C) & 0xFF])
        assert frames[1] == bytes([0x20, 0x01, UNITS_F, (0x20 + 0x01 + UNITS_F) & 0xFF])

    async def test_set_sound_writes_set_sound_frame(self) -> None:
        session, client = await self._open()
        try:
            await session.set_sound(False)
        finally:
            await session.__aexit__(None, None, None)

        frame = client.write_gatt_char.await_args.args[1]
        # CMD_SET_SOUND = 0x21; payload[0] = SOUND_OFF
        assert frame == bytes(
            [CMD_SET_SOUND, 0x01, SOUND_OFF, (CMD_SET_SOUND + 0x01 + SOUND_OFF) & 0xFF]
        )


@pytest.mark.asyncio
class TestTP902SessionNotifyDispatch:
    async def test_valid_frame_lands_on_queue(self) -> None:
        client = _make_client()
        session = TP902Session(
            _make_ble_device(), connector=AsyncMock(return_value=client)
        )
        async with session:
            # Status frame: cmd 0x26, len 0x03, units=C, beep on, batt 80
            payload = bytes([UNITS_C, SOUND_ON, 80])
            frame = bytes([0x26, 0x03]) + payload
            frame = frame + bytes([sum(frame) & 0xFF])
            session._on_notify(  # type: ignore[attr-defined]
                MagicMock(), bytearray(frame)
            )
            queue = await session.events()
            assert queue.qsize() == 1
            event = queue.get_nowait()
            assert isinstance(event, DeviceStatus)
            assert event.battery == 80
            assert event.beeper_on is True

    async def test_malformed_frame_is_dropped(self) -> None:
        client = _make_client()
        session = TP902Session(
            _make_ble_device(), connector=AsyncMock(return_value=client)
        )
        async with session:
            session._on_notify(  # type: ignore[attr-defined]
                MagicMock(), bytearray(b"\x00")
            )
            queue = await session.events()
            assert queue.empty()

    async def test_unknown_frame_hook_invoked(self) -> None:
        client = _make_client()
        session = TP902Session(
            _make_ble_device(), connector=AsyncMock(return_value=client)
        )
        seen: list[UnknownFrame] = []
        async with session:
            wrapped = await session.events(on_unknown=seen.append)
            unknown_frame = bytes([0x99, 0x01, 0x42])
            unknown_frame = unknown_frame + bytes([sum(unknown_frame) & 0xFF])
            session._on_notify(  # type: ignore[attr-defined]
                MagicMock(), bytearray(unknown_frame)
            )
            item = await wrapped.get()
            assert isinstance(item, UnknownFrame)
            assert item.cmd == 0x99
            assert seen and seen[0].cmd == 0x99


@pytest.mark.asyncio
async def test_tp902device_session_uses_injected_connector() -> None:
    """End-to-end: TP902Device.session() inherits the device's connector."""
    client = _make_client()
    connector = AsyncMock(return_value=client)
    device = TP902Device(_make_ble_device(), connector=connector)
    async with device.session() as session:
        assert session._client is client  # type: ignore[attr-defined]
    connector.assert_awaited_once()

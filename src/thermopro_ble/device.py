from __future__ import annotations

from datetime import datetime
from struct import pack
from uuid import UUID

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from .models import CAP_SET_DATETIME, has_capability, models_with_capability


class ThermoProDevice:
    """Helper for GATT operations against ThermoPro thermometers.

    ``DATETIME_SUPPORTED_MODELS`` is a snapshot of ``models.KNOWN_MODELS``
    taken at class-definition time. The registry is module-level immutable,
    so this is equivalent to a literal frozenset today, but mutating
    ``KNOWN_MODELS`` at runtime would not be reflected here.
    """

    datetime_uuid = UUID("00010203-0405-0607-0809-0a0b0c0d2b11")

    # Models known to accept the datetime GATT write. Sourced from the
    # central model registry; ``models_with_capability`` keeps this in sync
    # with ``models.KNOWN_MODELS`` so adding a new datetime-capable model
    # only requires updating one place. Snapshot semantics: see class docstring.
    DATETIME_SUPPORTED_MODELS: frozenset[str] = models_with_capability(CAP_SET_DATETIME)

    def __init__(self: ThermoProDevice, ble_device: BLEDevice):
        self.ble_device = ble_device

    @classmethod
    def supports_set_datetime(cls, model_or_name: str) -> bool:
        """Return True if the device model is known to accept set_datetime.

        Accepts either a bare model string ("TP358S") or an advertised device
        name ("TP358S (2142)"). Useful for downstream integrations that gate
        the datetime service on known-supported hardware.
        """
        return has_capability(model_or_name, CAP_SET_DATETIME)

    # ----
    # from https://github.com/koenvervloesem/bluetooth-clocks/
    # Copyright (c) 2023 Koen Vervloesem
    # MIT License
    # ----
    @staticmethod
    def pack_datetime(dt: datetime, am_pm: bool) -> bytes:
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("timezone aware datetime object expected")

        return pack(
            "BBBBBBBBBB",
            0xA5,
            dt.year % 2000,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.weekday() + 1,  # Monday-Sunday -> 0-6
            int(not am_pm),  # 1 means 24 hour format / 0 12 hour format
            0x5A,
        )

    # ----

    async def set_datetime(self: ThermoProDevice, dt: datetime, am_pm: bool) -> None:
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("timezone aware datetime object expected")

        client = await establish_connection(  # pragma: no cover
            BleakClient, self.ble_device, self.ble_device.address
        )

        try:
            await client.write_gatt_char(
                ThermoProDevice.datetime_uuid,
                ThermoProDevice.pack_datetime(dt, am_pm),
                True,
            )
        finally:
            await client.disconnect()

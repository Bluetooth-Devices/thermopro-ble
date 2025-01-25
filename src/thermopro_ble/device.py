from __future__ import annotations

from datetime import datetime
from struct import pack
from uuid import UUID

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection


class ThermoProDevice:
    datetime_uuid = UUID("00010203-0405-0607-0809-0a0b0c0d2b11")

    def __init__(self: ThermoProDevice, ble_device: BLEDevice):
        self.ble_device = ble_device

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

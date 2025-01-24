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
    def pack_datetime(dt: datetime, ampm: bool) -> bytes:
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
            int(not ampm),  # 1 means 24 hour format / 0 12 hour format
            0x5A,
        )

    # ----

    # not covered due to complex nature of mechanism
    async def connect(self: ThermoProDevice) -> BleakClient:
        return await establish_connection(  # pragma: no cover
            BleakClient, self.ble_device, self.ble_device.address
        )

    async def set_datetime(self: ThermoProDevice, dt: datetime, ampm: bool) -> None:
        client = await self.connect()

        try:
            await client.write_gatt_char(
                ThermoProDevice.datetime_uuid,
                ThermoProDevice.pack_datetime(dt, ampm),
                True,
            )
        finally:
            await client.disconnect()

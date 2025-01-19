from __future__ import annotations

from contextlib import AsyncExitStack
from datetime import datetime
from struct import pack
from uuid import UUID

from bleak import BleakClient
from bleak.backends.device import BLEDevice


class ThermoProDevice:
    datetime_uuid = UUID("00010203-0405-0607-0809-0a0b0c0d2b11")

    def __init__(self: ThermoProDevice, ble: BLEDevice):
        self.ble = ble
        self.stack = AsyncExitStack()
        self.client = None

    # required as otherwise linting is complaining about the return value
    async def _connect(self: ThermoProDevice, timeout: int = 30) -> BleakClient:
        return await self.stack.enter_async_context(
            BleakClient(self.ble, timeout=timeout)
        )

    async def connect(self: ThermoProDevice, timeout: int = 30) -> BleakClient:
        if not self.client:
            self.client = await self._connect(timeout=timeout)
        return self.client

    # ----
    # from https://github.com/koenvervloesem/bluetooth-clocks/
    # Copyright (c) 2023 Koen Vervloesem
    # MIT License
    # ----
    def pack_datetime(self: ThermoProDevice, dt: datetime, ampm: bool = False) -> bytes:
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

    async def set_datetime(self: ThermoProDevice, dt: datetime) -> None:
        client = await self.connect()
        await client.write_gatt_char(
            ThermoProDevice.datetime_uuid, self.pack_datetime(dt), True
        )

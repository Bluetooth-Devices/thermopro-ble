from __future__ import annotations

import asyncio

from typing import Any
from collections import Counter
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from datetime import datetime
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bluetooth_sensor_state_data import BluetoothServiceInfo, SensorUpdate
from sensor_state_data import (
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorValue,
    Units,
)

from thermopro_ble.device import ThermoProDevice

# where from?
BLE_DEVICE_DEFAULTS = {
    "name": None,
    "rssi": -127,
    "details": None,
}

def generate_ble_device(
    address: str | None = None,
    name: str | None = None,
    details: Any | None = None,
    rssi: int | None = None,
    **kwargs: Any,
) -> BLEDevice:
    """Generate a BLEDevice with defaults."""
    new = kwargs.copy()
    if address is not None:
        new["address"] = address
    if name is not None:
        new["name"] = name
    if details is not None:
        new["details"] = details
    if rssi is not None:
        new["rssi"] = rssi
    for key, value in BLE_DEVICE_DEFAULTS.items():
        new.setdefault(key, value)
    return BLEDevice(**new)
# end

class PackTestData:
    def __init__(self : PackTestData, name: str, dt : datetime, ampm: bool, packed : bytes):
        self.name = name
        self.dt = dt
        self.ampm = ampm
        self.packed = packed

    def test(self: PackTestData):
        result = ThermoProDevice.pack_datetime(self.dt, self.ampm)
        return result == self.packed, result, self.packed, self.name

    def generate(self: PackTestData):
        print(f"""PackTestDate("{self.name}", datetime.fromisoformat("{self.dt.replace(microsecond=0).isoformat()}"), {self.ampm}, {ThermoProDevice.pack_datetime(self.dt, ampm=self.ampm)}),""")

now = datetime.now()

PACK_TESTDATA = [
        PackTestData("self-test-24hour", now, False, ThermoProDevice.pack_datetime(now, False)),
        PackTestData("self-test-12hour", now, True, ThermoProDevice.pack_datetime(now, True)),
        PackTestData("2025-01-24-20:54:15-12", datetime.fromisoformat("2025-01-24T20:54:15"), True, b'\xa5\x19\x01\x18\x146\x0f\x05\x00Z'),
        PackTestData("2025-01-24-20:54:15-24", datetime.fromisoformat("2025-01-24T20:54:15"), False, b'\xa5\x19\x01\x18\x146\x0f\x05\x01Z'),
]

def create_send_mock():
    class ThermoProDeviceMock(ThermoProDevice):
        async def connect(self : ThermoProDeviceMock):
            client = BleakClient("")
            client.write_gatt_char = AsyncMock()
            client.disconnect = AsyncMock()
            self.client = client
            return client

    tpd = ThermoProDeviceMock(None)

    return tpd

class ThermoProDeviceTest(IsolatedAsyncioTestCase):
    def test_can_create(self: ThermoProDeviceTest):
        ThermoProDevice(generate_ble_device("aa:bb:cc:dd:ee:ff", "TP358"))


    def test_pack_cases(self: ThermoProDeviceTest):
        results = Counter()
        for idx, ptd in enumerate(PACK_TESTDATA):
            with self.subTest(i=idx):  # <----------------------
                passed, result, packed, name = ptd.test()
                self.assertTrue(passed, f"test '{name} failed - expected '{packed}' different from computed '{result}'")
                results[passed] += 1
        self.assertEqual(results[True], len(PACK_TESTDATA), msg="SCORE: %s / %s" % (results[True], len(PACK_TESTDATA)))

    async def test_device_send_24hour(self: ThermoProDeviceTest):
        tpd = create_send_mock()

        dt = datetime.now()

        await tpd.set_datetime(dt, False)

        tpd.client.write_gatt_char.assert_awaited_once_with(ThermoProDevice.datetime_uuid, ThermoProDevice.pack_datetime(dt, False), True)
        tpd.client.disconnect.assert_awaited_once()

    async def test_device_send_12hour(self: ThermoProDeviceTest):
        tpd = create_send_mock()

        dt = datetime.now()

        await tpd.set_datetime(dt, True)

        tpd.client.write_gatt_char.assert_awaited_once_with(ThermoProDevice.datetime_uuid, ThermoProDevice.pack_datetime(dt, True), True)
        tpd.client.disconnect.assert_awaited_once()


if __name__ == '__main__':
    for i in PACK_TESTDATA:
        i.generate()

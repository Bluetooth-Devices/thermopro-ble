from __future__ import annotations

import pytest

from typing import Any
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from bleak import BleakClient
from bleak.backends.device import BLEDevice

from thermopro_ble.device import ThermoProDevice

# Source https://github.com/sblibs/pySwitchbot/blob/master/tests/test_adv_parser.py
# Commit: bef9bebac1a17e8c989d343d40dca786535d149e
# Copyright (c) 2018 Daniel Høyer Iversen
# MIT License

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
    def __init__(
        self: PackTestData, name: str, dt: datetime, am_pm: bool, packed: bytes
    ):
        self.name = name
        self.dt = dt
        self.am_pm = am_pm
        self.packed = packed

    def test(self: PackTestData) -> tuple[bool, bytes, bytes, str]:
        result = ThermoProDevice.pack_datetime(self.dt, self.am_pm)
        return result == self.packed, result, self.packed, self.name

    def __repr__(self: PackTestData) -> str:
        return (
            f"""PackTestData("{self.name}", datetime.fromisoformat"""
            f"""("{self.dt.replace(microsecond=0).isoformat()}"), {self.am_pm}, """
            f"""{ThermoProDevice.pack_datetime(self.dt, self.am_pm)!r}),"""
        )

    def generate(self: PackTestData) -> None:
        print(str(self))


now = datetime.now(tz=timezone.utc)

PACK_TESTDATA = [
    PackTestData(
        "self-test-24hour", now, False, ThermoProDevice.pack_datetime(now, False)
    ),
    PackTestData(
        "self-test-12hour", now, True, ThermoProDevice.pack_datetime(now, True)
    ),
    PackTestData(
        "2025-01-24-20:54:15Z-12-hour",
        datetime.fromisoformat("2025-01-24T20:54:15+00:00"),
        True,
        b"\xa5\x19\x01\x18\x146\x0f\x05\x00Z",
    ),
    PackTestData(
        "2025-01-24-20:54:15Z-24hour",
        datetime.fromisoformat("2025-01-24T20:54:15+00:00"),
        False,
        b"\xa5\x19\x01\x18\x146\x0f\x05\x01Z",
    ),
    PackTestData(
        "2025-01-24-20:54:15+0200-12hour",
        datetime.fromisoformat("2025-01-24T20:54:15+02:00"),
        True,
        b"\xa5\x19\x01\x18\x146\x0f\x05\x00Z",
    ),
    PackTestData(
        "2025-01-24-20:54:15+02:00-24hour",
        datetime.fromisoformat("2025-01-24T20:54:15+02:00"),
        False,
        b"\xa5\x19\x01\x18\x146\x0f\x05\x01Z",
    ),
]


@pytest.fixture()
def dummy_device() -> ThermoProDevice:
    return ThermoProDevice(generate_ble_device("aa:bb:cc:dd:ee:ff", "TP358"))


@pytest.fixture()
def mock_bleak_client(monkeypatch: pytest.MonkeyPatch) -> BleakClient:
    client = BleakClient("")
    client.write_gatt_char = AsyncMock()
    client.disconnect = AsyncMock()

    monkeypatch.setattr(
        "thermopro_ble.device.establish_connection", AsyncMock(return_value=client)
    )

    return client


def test_can_create(dummy_device: ThermoProDevice) -> None:
    assert isinstance(dummy_device, ThermoProDevice), "device could not be created"


def test_non_timezone_aware_datetime_pack() -> None:
    with pytest.raises(ValueError) as exc_info:
        ThermoProDevice.pack_datetime(
            datetime.fromisoformat("2025-01-24T20:54:15"), False
        )

    assert str(exc_info.value) == "timezone aware datetime object expected", (
        "pack_datetime should have rejected naive datetime"
    )


@pytest.mark.parametrize("pack_test", PACK_TESTDATA, ids=lambda val: val.name)
def test_pack_cases(pack_test: PackTestData) -> None:
    passed, result, packed, name = pack_test.test()
    assert passed, (
        f"test '{name} failed - expected '{packed!r}' different"
        f"from computed '{result!r}'",
    )


@pytest.mark.asyncio
async def test_device_send_24hour(
    mock_bleak_client: BleakClient, dummy_device: ThermoProDevice
) -> None:
    dt = datetime.now(tz=timezone.utc)

    await dummy_device.set_datetime(dt, False)

    mock_bleak_client.write_gatt_char.assert_awaited_once_with(
        ThermoProDevice.datetime_uuid,
        ThermoProDevice.pack_datetime(dt, False),
        True,
    )
    mock_bleak_client.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_device_send_12hour(
    mock_bleak_client: BleakClient, dummy_device: ThermoProDevice
) -> None:
    dt = datetime.now(tz=timezone.utc)

    await dummy_device.set_datetime(dt, True)

    mock_bleak_client.write_gatt_char.assert_awaited_once_with(
        ThermoProDevice.datetime_uuid, ThermoProDevice.pack_datetime(dt, True), True
    )
    mock_bleak_client.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_non_timezone_aware_datetime_set(
    mock_bleak_client: BleakClient, dummy_device: ThermoProDevice
) -> None:
    with pytest.raises(ValueError) as exc_info:
        await dummy_device.set_datetime(
            datetime.fromisoformat("2025-01-24T20:54:15"), True
        )

    assert str(exc_info.value) == "timezone aware datetime object expected", (
        "pack_datetime should have rejected naive datetime"
    )


if __name__ == "__main__":
    for i in PACK_TESTDATA:
        i.generate()

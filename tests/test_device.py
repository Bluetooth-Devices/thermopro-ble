from __future__ import annotations

import pytest

from typing import Any
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from bleak import BleakClient
from bleak.backends.device import BLEDevice

from thermopro_ble.device import ThermoProDevice

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


now = datetime.now(tz=timezone.utc)

PACK_TESTDATA = [
    ("self-test-24hour", now, False, ThermoProDevice.pack_datetime(now, False)),
    ("self-test-12hour", now, True, ThermoProDevice.pack_datetime(now, True)),
    (
        "2025-01-24-20:54:15Z-12-hour",
        datetime.fromisoformat("2025-01-24T20:54:15+00:00"),
        True,
        b"\xa5\x19\x01\x18\x146\x0f\x05\x00Z",
    ),
    (
        "2025-01-24-20:54:15Z-24hour",
        datetime.fromisoformat("2025-01-24T20:54:15+00:00"),
        False,
        b"\xa5\x19\x01\x18\x146\x0f\x05\x01Z",
    ),
    (
        "2024-03-18-10:23:46+0200-12hour",
        datetime.fromisoformat("2024-03-18T10:23:46+02:00"),
        True,
        b"\xa5\x18\x03\x12\n\x17.\x01\x00Z",
    ),
    (
        "2024-03-18-10:23:46+0200-24hour",
        datetime.fromisoformat("2024-03-18T10:23:46+02:00"),
        False,
        b"\xa5\x18\x03\x12\n\x17.\x01\x01Z",
    ),
]


@pytest.fixture()
def dummy_client(monkeypatch: pytest.MonkeyPatch) -> BleakClient:
    client = BleakClient("")
    monkeypatch.setattr(client, "write_gatt_char", AsyncMock())
    monkeypatch.setattr(client, "disconnect", AsyncMock())
    return client


@pytest.fixture()
def dummy_device() -> ThermoProDevice:
    return ThermoProDevice(generate_ble_device("aa:bb:cc:dd:ee:ff", "TP358"))


@pytest.fixture()
def mock_bleak_client(
    monkeypatch: pytest.MonkeyPatch, dummy_client: BleakClient
) -> BleakClient:
    monkeypatch.setattr(
        "thermopro_ble.device.establish_connection",
        AsyncMock(return_value=dummy_client),
    )

    return dummy_client


def test_can_create(dummy_device: ThermoProDevice) -> None:
    assert isinstance(dummy_device, ThermoProDevice), "device could not be created"


def test_non_timezone_aware_datetime_pack() -> None:
    with pytest.raises(ValueError, match="timezone aware datetime object expected"):
        ThermoProDevice.pack_datetime(
            datetime.fromisoformat("2025-01-24T20:54:15"), False
        )


# to keep stability across test runs, use just the name(only str) here
@pytest.mark.parametrize(
    "name,dt,am_pm,packed",
    PACK_TESTDATA,
    ids=lambda val: val if isinstance(val, str) else "",
)
def test_pack_cases(name: str, dt: datetime, am_pm: bool, packed: bytes) -> None:
    computed = ThermoProDevice.pack_datetime(dt, am_pm)
    assert computed == packed, (
        f"test '{name} failed - expected '{packed!r}' different"
        f"from computed '{computed!r}'",
    )


def test_timezone_difference():
    assert ThermoProDevice.pack_datetime(
        datetime.fromisoformat("2024-03-18-10:23:46+02:00"), False
    ) != ThermoProDevice.pack_datetime(
        datetime.fromisoformat("2024-03-18-08:23:46+00:00"), False
    ), "timezone aware datetime must have localized time fields"


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
    with pytest.raises(ValueError, match="timezone aware datetime object expected"):
        await dummy_device.set_datetime(
            datetime.fromisoformat("2025-01-24T20:54:15"), True
        )


if __name__ == "__main__":
    for name, dt, am_pm, packed in PACK_TESTDATA:
        print(
            f"('{name}', datetime.fromisoformat"
            f"('{dt.replace(microsecond=0).isoformat()}'), {am_pm}, "
            f"{ThermoProDevice.pack_datetime(dt, am_pm)!r}),"
        )

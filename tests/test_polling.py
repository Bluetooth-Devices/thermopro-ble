"""Tests for the fallback GATT polling support."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest
from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bluetooth_data_tools import monotonic_time_coarse
from thermopro_ble.parser import (
    MIN_POLL_INTERVAL,
    ThermoProBluetoothDeviceData,
)

from tests.test_parser import (
    TP357,
    TP960R,
    make_bluetooth_service_info,
)

BLE_DEVICE_DEFAULTS: dict[str, Any] = {"name": None, "rssi": -127, "details": None}


def _make_ble_device(
    address: str = "aa:bb:cc:dd:ee:ff", name: str | None = "TP357"
) -> BLEDevice:
    kwargs = dict(BLE_DEVICE_DEFAULTS)
    kwargs.update(address=address, name=name)
    return BLEDevice(**kwargs)


def test_supports_polling_unknown_device() -> None:
    """An untouched parser has no device type and cannot be polled."""
    parser = ThermoProBluetoothDeviceData()
    assert parser.supports_polling is False
    assert parser.poll_needed(TP357, None) is False


def test_supports_polling_tp357() -> None:
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP357)
    assert parser.supports_polling is True


def test_supports_polling_excludes_tp96() -> None:
    """TP96/TP97 families are not enrolled in fallback polling yet."""
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP960R)
    assert parser.supports_polling is False
    assert parser.poll_needed(TP960R, None) is False


def test_last_full_update_is_set_after_successful_parse() -> None:
    parser = ThermoProBluetoothDeviceData()
    assert parser._last_full_update == 0.0
    parser.update(TP357)
    assert parser._last_full_update == TP357.time


def test_poll_needed_when_no_update_seen() -> None:
    parser = ThermoProBluetoothDeviceData()
    parser._device_type = "TP357"
    assert parser.poll_needed(TP357, None) is True


def test_poll_not_needed_when_advertisement_is_fresh() -> None:
    """A recently updated parser should not request a poll."""
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP357)
    fresh_info = make_bluetooth_service_info(
        name="TP357 (2142)",
        manufacturer_data={61890: b"\x00\x1d\x02,"},
        service_uuids=[],
        address="aa:bb:cc:dd:ee:ff",
        rssi=-60,
        service_data={},
        source="local",
    )
    assert parser.poll_needed(fresh_info, None) is False


def test_poll_needed_when_advertisement_is_stale() -> None:
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP357)
    # Move the recorded update timestamp into the past beyond the threshold.
    parser._last_full_update = monotonic_time_coarse() - (MIN_POLL_INTERVAL + 10)
    assert parser.poll_needed(TP357, None) is True


@pytest.mark.asyncio
async def test_async_poll_connects_and_disconnects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """async_poll should call establish_connection and then disconnect."""
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP357)

    client = BleakClient("")
    disconnect_mock = AsyncMock()
    monkeypatch.setattr(client, "disconnect", disconnect_mock)
    establish = AsyncMock(return_value=client)
    monkeypatch.setattr(
        "thermopro_ble.parser.establish_connection", establish
    )

    result = await parser.async_poll(_make_ble_device())

    establish.assert_awaited_once()
    disconnect_mock.assert_awaited_once()
    # Result should be a SensorUpdate-shaped object (devices/entity_descriptions).
    assert hasattr(result, "devices")
    assert hasattr(result, "entity_descriptions")


@pytest.mark.asyncio
async def test_async_poll_swallows_connect_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Connection errors should not propagate out of async_poll."""
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP357)

    establish = AsyncMock(side_effect=BleakError("nope"))
    monkeypatch.setattr(
        "thermopro_ble.parser.establish_connection", establish
    )

    # Should not raise.
    result = await parser.async_poll(_make_ble_device())
    establish.assert_awaited_once()
    assert hasattr(result, "devices")


@pytest.mark.asyncio
async def test_async_poll_swallows_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP357)

    establish = AsyncMock(side_effect=TimeoutError())
    monkeypatch.setattr(
        "thermopro_ble.parser.establish_connection", establish
    )

    result = await parser.async_poll(_make_ble_device())
    assert hasattr(result, "devices")


@pytest.mark.asyncio
async def test_async_poll_swallows_disconnect_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure during disconnect must not bubble up."""
    parser = ThermoProBluetoothDeviceData()
    parser.update(TP357)

    client = BleakClient("")
    monkeypatch.setattr(
        client, "disconnect", AsyncMock(side_effect=BleakError("boom"))
    )
    monkeypatch.setattr(
        "thermopro_ble.parser.establish_connection",
        AsyncMock(return_value=client),
    )

    result = await parser.async_poll(_make_ble_device())
    assert hasattr(result, "devices")

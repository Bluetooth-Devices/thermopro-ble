"""Parser for ThermoPro BLE advertisements."""

from __future__ import annotations

from sensor_state_data import (
    BinarySensorDeviceClass,
    BinarySensorValue,
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorUpdate,
    SensorValue,
    Units,
)

from .device import ThermoProDevice
from .parser import ThermoProBluetoothDeviceData

__version__ = "1.1.4"

__all__ = [
    "BinarySensorDeviceClass",
    "BinarySensorValue",
    "DeviceKey",
    "SensorDescription",
    "SensorDeviceClass",
    "SensorDeviceInfo",
    "SensorUpdate",
    "SensorValue",
    "ThermoProBluetoothDeviceData",
    "ThermoProDevice",
    "Units",
]

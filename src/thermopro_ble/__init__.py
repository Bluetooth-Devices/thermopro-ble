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
from .tp902 import (
    AlarmConfig,
    AuthResponse,
    DeviceStatus,
    FirmwareVersion,
    TemperatureBroadcast,
    TemperatureSnapshot,
    TP902Device,
    UnknownFrame,
)

__version__ = "1.1.4"

__all__ = [
    "AlarmConfig",
    "AuthResponse",
    "BinarySensorDeviceClass",
    "BinarySensorValue",
    "DeviceKey",
    "DeviceStatus",
    "FirmwareVersion",
    "SensorDescription",
    "SensorDeviceClass",
    "SensorDeviceInfo",
    "SensorUpdate",
    "SensorValue",
    "TP902Device",
    "TemperatureBroadcast",
    "TemperatureSnapshot",
    "ThermoProBluetoothDeviceData",
    "ThermoProDevice",
    "UnknownFrame",
    "Units",
]

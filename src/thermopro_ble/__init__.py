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
from .models import (
    KNOWN_MODELS,
    ThermoProModel,
    get_model,
    has_capability,
    is_supported_model,
)
from .parser import ThermoProBluetoothDeviceData

__version__ = "1.1.4"

__all__ = [
    "ThermoProDevice",
    "ThermoProBluetoothDeviceData",
    "ThermoProModel",
    "KNOWN_MODELS",
    "get_model",
    "has_capability",
    "is_supported_model",
    "BinarySensorDeviceClass",
    "BinarySensorValue",
    "SensorDescription",
    "SensorDeviceInfo",
    "DeviceKey",
    "SensorUpdate",
    "SensorDeviceClass",
    "SensorDeviceInfo",
    "SensorValue",
    "Units",
]

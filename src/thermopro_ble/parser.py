"""Parser for ThermoPro BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/thermopro.py

MIT License applies.
"""
from __future__ import annotations

import logging
from struct import Struct

from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import SensorLibrary

# from bluetooth_data_tools import short_address

_LOGGER = logging.getLogger(__name__)


UNPACK = Struct("<hB").unpack


def short_address(address: str) -> str:
    """Convert a Bluetooth address to a short address."""
    split_address = address.replace("-", ":").split(":")
    return f"{split_address[-2].upper()}{split_address[-1].upper()}"[-4:]


class ThermoProBluetoothDeviceData(BluetoothData):
    """Date update for ThermoPro Bluetooth devices."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing thermopro BLE advertisement data: %s", service_info)
        if not service_info.name.startswith("TP35"):
            return

        changed_manufacturer_data = self.changed_manufacturer_data(service_info)

        if not changed_manufacturer_data:
            return

        last_id = list(changed_manufacturer_data)[-1]
        data = (
            int(last_id).to_bytes(2, byteorder="little")
            + changed_manufacturer_data[last_id]
        )

        if len(data) != 6:
            return

        (temp, humi) = UNPACK(data[1:4])
        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp / 10)
        self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi)
        self.set_title(f"{service_info.name} {short_address(service_info.address)}")
        self.set_device_name(service_info.name)
        self.set_device_manufacturer("ThermoPro")

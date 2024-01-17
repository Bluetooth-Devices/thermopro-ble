"""Parser for ThermoPro BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/thermopro.py

MIT License applies.
"""
from __future__ import annotations

import logging
from struct import Struct

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import SensorLibrary

_LOGGER = logging.getLogger(__name__)


BATTERY_VALUE_TO_LEVEL = {
    0: 1,
    1: 50,
    2: 100,
}

UNPACK_TEMP_HUMID = Struct("<hB").unpack
UNPACK_SPIKE_TEMP = Struct("<BHHH").unpack

MULTIPROBE_DEVICES = {
    "TP962R": {
        0: "black",
        1: "white",
    },
}


class ThermoProBluetoothDeviceData(BluetoothData):
    """Date update for ThermoPro Bluetooth devices."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing thermopro BLE advertisement data: %s", service_info)
        name = service_info.name
        if not name.startswith(("TP35", "TP39", "TP96")):
            return
        if not service_info.manufacturer_data:
            return
        if len(list(service_info.manufacturer_data.values())[0]) < 4:
            return
        self.set_device_type(name.split(" ")[0])
        self.set_title(f"{name} {short_address(service_info.address)}")
        self.set_device_name(name)
        self.set_precision(2)
        self.set_device_manufacturer("ThermoPro")
        changed_manufacturer_data = self.changed_manufacturer_data(service_info)

        if not changed_manufacturer_data or len(changed_manufacturer_data) > 1:
            # If len(changed_manufacturer_data) > 1 it means we switched
            # ble adapters so we do not know which data is the latest
            # and we need to wait for the next update.
            return

        last_id = list(changed_manufacturer_data)[-1]
        data = (
            int(last_id).to_bytes(2, byteorder="little")
            + changed_manufacturer_data[last_id]
        )

        if len(data) < 6:
            return

        if name.startswith("TP96"):
            MAX_BAT = 2880
            MIN_BAT = 1600  # ??
            bat_range = MAX_BAT - MIN_BAT
            (probe_index, internal_temp, battery, ambient_temp) = UNPACK_SPIKE_TEMP(
                data
            )
            internal_temp = internal_temp - 30
            ambient_temp = ambient_temp - 30
            battery_percent = (battery - MIN_BAT) / bat_range

            multiprobe_mapping = MULTIPROBE_DEVICES.get(name, {0: ""})
            probe_name = multiprobe_mapping.get(probe_index, str(probe_index))
            if probe_name:
                self.set_title(
                    f"{name} {probe_name.capitalize()} "
                    f"{short_address(service_info.address)}"
                )
                self.set_device_name(f"{name}_{probe_name.upper()}")

            # TP96 has a different format
            # It has an internal temp probe and an ambient temp probe
            self.update_predefined_sensor(
                SensorLibrary.TEMPERATURE__CELSIUS,
                internal_temp,
                key="internal_temperature",
                name="Internal Temperature",
            )
            self.update_predefined_sensor(
                SensorLibrary.TEMPERATURE__CELSIUS,
                ambient_temp,
                key="ambient_temperature",
                name="Ambient Temperature",
            )
            self.update_predefined_sensor(
                SensorLibrary.BATTERY__PERCENTAGE, battery_percent
            )

            return

        # TP357S seems to be in 6, TP397 and TP393 in 4
        battery_byte = data[6] if len(data) == 7 else data[4]
        if battery_byte in BATTERY_VALUE_TO_LEVEL:
            self.update_predefined_sensor(
                SensorLibrary.BATTERY__PERCENTAGE,
                BATTERY_VALUE_TO_LEVEL[battery_byte],
            )

        (temp, humi) = UNPACK_TEMP_HUMID(data[1:4])
        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp / 10)
        self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi)

"""
Parser for ThermoPro BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/thermopro.py

MIT License applies.
"""

from __future__ import annotations

import logging
from math import tanh
from struct import Struct, error as struct_error

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from sensor_state_data import SensorLibrary

from habluetooth import BluetoothServiceInfoBleak

_LOGGER = logging.getLogger(__name__)


BATTERY_VALUE_TO_LEVEL = {
    0: 1,
    1: 50,
    2: 100,
}

UNPACK_TEMP_HUMID = Struct("<hB").unpack
UNPACK_SPIKE_TEMP = Struct("<BHHH").unpack


# TP96x battery values appear to be a voltage reading, probably in millivolts.
# This means that calculating battery life from it is a non-linear function.
# Examining the curve, it looked fairly close to a curve from the tanh function.
# So, I created a script to use Tensorflow to optimize an equation in the format
# A*tanh(B*x+C)+D
# Where A,B,C,D are the variables to optimize for.  This yielded the below function
def tp96_battery(voltage: int) -> float:
    raw = 52.317286 * tanh(voltage / 273.624277936 - 8.76485439394) + 51.06925
    clamped = max(0, min(raw, 100))
    return round(clamped, 2)


class ThermoProBluetoothDeviceData(BluetoothData):
    """Date update for ThermoPro Bluetooth devices."""

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing thermopro BLE advertisement data: %s", service_info)
        name = service_info.name
        if not name.startswith(("TP35", "TP39", "TP96", "TP97")):
            return

        model = name.split(" ")[0]
        self.set_device_type(model)
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

        if name.startswith(("TP96", "TP97")):
            # TP96 has a different format
            # It has an internal temp probe and an ambient temp probe
            try:
                (
                    probe_zero_indexed,
                    internal_temp,
                    battery_voltage,
                    ambient_temp,
                ) = UNPACK_SPIKE_TEMP(data)
            except struct_error:
                _LOGGER.error("Error parsing data from probe: %s", data)
                return

            probe_one_indexed = probe_zero_indexed + 1
            internal_temp = internal_temp - 30
            ambient_temp = ambient_temp - 30
            battery_percent = tp96_battery(battery_voltage)
            self.update_predefined_sensor(
                SensorLibrary.TEMPERATURE__CELSIUS,
                internal_temp,
                key=f"internal_temperature_probe_{probe_one_indexed}",
                name=f"Probe {probe_one_indexed} Internal Temperature",
            )
            self.update_predefined_sensor(
                SensorLibrary.TEMPERATURE__CELSIUS,
                ambient_temp,
                key=f"ambient_temperature_probe_{probe_one_indexed}",
                name=f"Probe {probe_one_indexed} Ambient Temperature",
            )
            self.set_precision(0)
            self.update_predefined_sensor(
                SensorLibrary.BATTERY__PERCENTAGE,
                battery_percent,
                key=f"battery_probe_{probe_one_indexed}",
                name=f"Probe {probe_one_indexed} Battery",
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

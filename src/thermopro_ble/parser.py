"""
Parser for ThermoPro BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/thermopro.py

MIT License applies.
"""

from __future__ import annotations

import contextlib
import logging
from math import tanh
from struct import Struct

from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from bluetooth_data_tools import monotonic_time_coarse, short_address
from bluetooth_sensor_state_data import BluetoothData
from sensor_state_data import SensorLibrary, SensorUpdate

from habluetooth import BluetoothServiceInfoBleak

_LOGGER = logging.getLogger(__name__)

# Minimum interval between forced GATT polls (seconds). If we have not seen a
# fresh advertisement within this window, ``poll_needed`` will return True.
MIN_POLL_INTERVAL = 180.0

# Device name prefixes for which we are willing to attempt a GATT wake-up poll.
# These are the ThermoPro families known to broadcast sensor data passively but
# occasionally go quiet — connecting briefly nudges them back into advertising.
POLLABLE_NAME_PREFIXES = ("TP35", "TP39")


BATTERY_VALUE_TO_LEVEL = {
    0: 1,
    1: 50,
    2: 100,
}

UNPACK_TEMP_HUMID = Struct("<hB").unpack
UNPACK_SPIKE_TEMP = Struct("<BHHH").unpack
UNPACK_SPIKE_PRO_TEMP = Struct("<BHHfffHHH").unpack


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


# TP97x only supply temperatures in F, even when display is set to celsius
def fahrenheit_to_celsius(fahrenheit_temp: float) -> float:
    celsius_temp = (fahrenheit_temp - 32) * 5 / 9
    return round(celsius_temp, 1)


class ThermoProBluetoothDeviceData(BluetoothData):
    """Date update for ThermoPro Bluetooth devices."""

    def __init__(self) -> None:
        """Initialize the parser."""
        super().__init__()
        # Monotonic timestamp of the last advertisement we successfully parsed.
        # Used by ``poll_needed`` to decide whether to force a GATT poll.
        self._last_full_update: float = 0.0
        # Cached device model string ("TP357", "TP358S", ...) once known.
        self._device_type: str | None = None

    def _update_sensors(
        self,
        probe_one_indexed: int,
        internal_temp: int,
        ambient_temp: int,
        battery_percent: float,
    ) -> None:
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

    def _update_sensors_tp97(
        self,
        probe_one_indexed: int,
        internal_temp_tip: float,
        internal_temp_center: float,
        internal_temp_end: float,
        ambient_temp: float,
        battery_percent: float,
    ) -> None:
        self.set_precision(1)
        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS,
            internal_temp_tip,
            key=f"internal_temperature_probe_{probe_one_indexed}",
            name=f"Probe {probe_one_indexed} Internal Tip Temperature",
        )
        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS,
            internal_temp_center,
            key=f"internal_center_temperature_probe_{probe_one_indexed}",
            name=f"Probe {probe_one_indexed} Internal Center Temperature",
        )
        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS,
            internal_temp_end,
            key=f"internal_end_temperature_probe_{probe_one_indexed}",
            name=f"Probe {probe_one_indexed} Internal End Temperature",
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

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing thermopro BLE advertisement data: %s", service_info)
        name = service_info.name
        if not name.startswith(("TP35", "TP39", "TP96", "TP97")):
            return

        model = name.split(" ")[0]
        self._device_type = model
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

        data_length = len(data)

        if data_length == 23 and name.startswith("TP97"):
            # TP972 has a 23-byte format
            # It has an internal temp probe and an ambient temp probe
            (
                probe_zero_indexed,
                ambient_temp,
                battery_voltage,
                internal_tip_temp,  # tip temperature
                internal_center_temp,  # center temperature
                internal_end_temp,  # end temperature
                _,  # looks like a static id
                _,
                _,
            ) = UNPACK_SPIKE_PRO_TEMP(data)

            probe_one_indexed = probe_zero_indexed + 1
            internal_tip_temp = fahrenheit_to_celsius(internal_tip_temp - 54)
            internal_center_temp = fahrenheit_to_celsius(internal_center_temp - 54)
            internal_end_temp = fahrenheit_to_celsius(internal_end_temp - 54)
            ambient_temp = int(fahrenheit_to_celsius(ambient_temp - 54))
            battery_percent = tp96_battery(battery_voltage)
            self._update_sensors_tp97(
                probe_one_indexed,
                internal_tip_temp,
                internal_center_temp,
                internal_end_temp,
                ambient_temp,
                battery_percent,
            )
            self._last_full_update = service_info.time
            return

        if data_length in (7, 13) and name.startswith(("TP96", "TP97")):
            # TP96 has a different format that is shared with TP970
            # It has an internal temp probe and an ambient temp probe
            # Some probes append 6 extra bytes (observed to be the reversed
            # base-station MAC address) after the standard 7-byte payload,
            # yielding 13 bytes total. The extra bytes are ignored.
            (
                probe_zero_indexed,
                internal_temp,
                battery_voltage,
                ambient_temp,
            ) = UNPACK_SPIKE_TEMP(data[:7])

            probe_one_indexed = probe_zero_indexed + 1
            internal_temp = internal_temp - 30
            ambient_temp = ambient_temp - 30
            battery_percent = tp96_battery(battery_voltage)
            self._update_sensors(
                probe_one_indexed, internal_temp, ambient_temp, battery_percent
            )
            self._last_full_update = service_info.time
            return

        # TP357S, TP397 and TP393
        if data_length >= 6 and name.startswith("TP3"):
            # battery value is represented by the lower two bits of byte 4
            # (verified with TP357S on laboratory power supply)
            battery_value = data[4] & 3
            if battery_value in BATTERY_VALUE_TO_LEVEL:
                self.update_predefined_sensor(
                    SensorLibrary.BATTERY__PERCENTAGE,
                    BATTERY_VALUE_TO_LEVEL[battery_value],
                )

            # TP357S could report invalid temperature and humidity values
            # filter them out
            temp_humi = data[1:4]
            if temp_humi == b"\xff\xff\xff":
                return

            (temp, humi) = UNPACK_TEMP_HUMID(temp_humi)
            self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp / 10)
            self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi)
            self._last_full_update = service_info.time
            return

        _LOGGER.error("Error parsing data from probe: %s", data)

    @property
    def supports_polling(self) -> bool:
        """Whether the active device model supports the fallback GATT poll."""
        return self._device_type is not None and self._device_type.startswith(
            POLLABLE_NAME_PREFIXES
        )

    def poll_needed(
        self,
        service_info: BluetoothServiceInfoBleak,
        last_poll: float | None,
    ) -> bool:
        """
        Whether a GATT poll should be performed.

        Returns True for supported models when we have not seen a fresh
        advertisement within ``MIN_POLL_INTERVAL`` seconds. Mirrors the
        pattern used by ``inkbird-ble``.
        """
        if not self.supports_polling:
            return False
        if not self._last_full_update:
            return True
        return (monotonic_time_coarse() - self._last_full_update) > MIN_POLL_INTERVAL

    async def async_poll(self, ble_device: BLEDevice) -> SensorUpdate:
        """
        Wake a quiet ThermoPro device with a brief GATT connection.

        ThermoPro sensors in the TP35x / TP39x families broadcast their
        readings passively. Some units occasionally stop advertising for
        long stretches (see Home Assistant core#136034). Establishing a
        short-lived GATT connection nudges them back into advertising,
        after which the advertisement parser resumes producing updates.

        Per-model GATT decoding is intentionally left out for now —
        adding it requires verified packet captures and can be layered
        on top of this scaffolding in follow-up work.
        """
        _LOGGER.debug("Polling ThermoPro device %s", ble_device.address)
        try:
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                ble_device.name or ble_device.address,
            )
        except (BleakError, TimeoutError) as err:
            _LOGGER.debug(
                "Error connecting to ThermoPro device %s: %s",
                ble_device.address,
                err,
            )
            return self._finish_update()

        with contextlib.suppress(BleakError, TimeoutError):
            await client.disconnect()
        return self._finish_update()

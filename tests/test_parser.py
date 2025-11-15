from uuid import UUID

from bluetooth_data_tools import monotonic_time_coarse
from bluetooth_sensor_state_data import SensorUpdate
from sensor_state_data import (
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorValue,
    Units,
)
from thermopro_ble.parser import ThermoProBluetoothDeviceData

from bleak.backends.device import BLEDevice
from habluetooth import BluetoothServiceInfoBleak


def make_bluetooth_service_info(
    name: str,
    manufacturer_data: dict[int, bytes],
    service_uuids: list[str],
    address: str,
    rssi: int,
    service_data: dict[UUID, bytes],
    source: str,
    tx_power: int = 0,
    raw: bytes | None = None,
) -> BluetoothServiceInfoBleak:
    return BluetoothServiceInfoBleak(
        name=name,
        manufacturer_data=manufacturer_data,
        service_uuids=service_uuids,
        address=address,
        rssi=rssi,
        service_data=service_data,
        source=source,
        device=BLEDevice(
            name=name,
            address=address,
            details={},
            rssi=rssi,
        ),
        time=monotonic_time_coarse(),
        advertisement=None,
        connectable=True,
        tx_power=tx_power,
        raw=raw,
    )


def test_can_create():
    ThermoProBluetoothDeviceData()


TP357 = make_bluetooth_service_info(
    name="TP357 (2142)",
    manufacturer_data={61890: b"\x00\x1d\x02,"},
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
)


TP357_RAW = make_bluetooth_service_info(
    name="TP357 (2142)",
    manufacturer_data={1: b"\x02,"},
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
    raw=b"\x07\xff\x82\xf1\x00\x1d\x02,",
)

TP357_ADD = make_bluetooth_service_info(
    name="TP357 (2142)",
    manufacturer_data={63938: b"\x00\x10\x02,"},
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
)

TP357_S = make_bluetooth_service_info(
    name="TP357S (2142)",
    manufacturer_data={
        61122: b'\x00)"\x0b\x01',
    },
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
)


TP357_S_2 = make_bluetooth_service_info(
    name="TP357S (2142)",
    manufacturer_data={
        61122: b'\x00)"\x0b\x01',
        60866: b'\x00)"\x0b\x01',
        60610: b'\x00)"\x0b\x01',
        60354: b'\x00("\x0b\x01',
        60098: b'\x00("\x0b\x01',
        59842: b'\x00)"\x0b\x01',
        59586: b'\x00("\x0b\x01',
        59330: b'\x00("\x0b\x01',
        59074: b'\x00("\x0b\x01',
        58818: b'\x00("\x0b\x01',
        58562: b"\x00'\"\x0b\x01",
        58306: b'\x00("\x0b\x01',
        58050: b'\x00("\x0b\x01',
        57794: b'\x00)"\x0b\x01',
        57538: b'\x00)"\x0b\x01',
        57282: b'\x00)"\x0b\x01',
        57026: b'\x00)"\x0b\x01',
        56770: b'\x00)"\x0b\x01',
        56514: b'\x00)"\x0b\x01',
        56258: b'\x00)"\x0b\x01',
        56002: b'\x00)"\x0b\x01',
        55746: b'\x00*"\x0b\x01',
        55490: b'\x00)"\x0b\x01',
        55234: b'\x00*"\x0b\x01',
        54978: b'\x00*"\x0b\x01',
        54722: b'\x00*"\x0b\x01',
        54466: b'\x00+"\x0b\x01',
        54210: b'\x00-"\x0b\x01',
        53954: b'\x00,"\x0b\x01',
        53698: b'\x00/"\x0b\x01',
        53442: b'\x001"\x0b\x01',
        53186: b'\x00."\x0b\x01',
        52930: b'\x00,"\x0b\x01',
        52674: b'\x00,"\x0b\x01',
        52418: b'\x00+"\x0b\x01',
        52162: b'\x00*"\x0b\x01',
        51906: b'\x00*"\x0b\x01',
        51650: b'\x00*"\x0b\x01',
        51394: b'\x00*"\x0b\x01',
        51138: b'\x00*"\x0b\x01',
        50882: b'\x00)"\x0b\x01',
    },
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
)


TP393 = make_bluetooth_service_info(
    name="TP393 (9376)",
    manufacturer_data={62146: b"\x005\x02,"},
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
)


TP393_DETECT_CHANGED_1 = make_bluetooth_service_info(
    name="TP393 (9376)",
    manufacturer_data={
        194: b"\x00\x00\x00,",
        62146: b"\x00(\x02,",
        61890: b"\x00(\x02,",
        61634: b"\x00(\x02,",
        61378: b"\x00(\x02,",
        61122: b"\x00(\x02,",
        60866: b"\x00(\x02,",
        60610: b"\x00(\x02,",
        60354: b"\x00)\x02,",
        60098: b"\x00)\x02,",
        59842: b"\x00)\x02,",
        59586: b"\x00)\x02,",
        59330: b"\x00*\x02,",
        59074: b"\x00*\x02,",
        58818: b"\x00*\x02,",
        58562: b"\x00*\x02,",
    },
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
)

TP393_DETECT_CHANGED_2 = make_bluetooth_service_info(
    name="TP393 (9376)",
    manufacturer_data={
        194: b"\x00\x00\x00,",
        62146: b"\x00(\x02,",
        61890: b"\x00(\x02,",
        61634: b"\x00(\x02,",
        61378: b"\x00(\x02,",
        61122: b"\x00(\x02,",
        60866: b"\x00(\x02,",
        60610: b"\x00(\x02,",
        60354: b"\x00)\x02,",
        60098: b"\x00)\x02,",
        59842: b"\x00)\x02,",
        59586: b"\x00)\x02,",
        59330: b"\x00*\x02,",
        59074: b"\x00*\x02,",
        58818: b"\x00*\x02,",
        58562: b"\x00*\x02,",
    },
    service_uuids=[],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    source="local",
)

TP960R = make_bluetooth_service_info(
    name="TP960R (0000)",
    manufacturer_data={14848: b"\x000\x088\x00"},
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-75,
    service_data={},
    source="local",
)
TP960R_2 = make_bluetooth_service_info(
    name="TP960R (0000)",
    manufacturer_data={
        14848: b"\x000\x088\x00",
        14336: b'\x00"\x088\x00',
        14592: b'\x00"\x089\x00',
    },
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-75,
    service_data={},
    source="local",
)

TP962R = make_bluetooth_service_info(
    name="TP962R (0000)",
    manufacturer_data={14081: b"\x00;\x0b7\x00"},
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-52,
    service_data={},
    source="local",
)
TP962R_2 = make_bluetooth_service_info(
    name="TP962R (0000)",
    manufacturer_data={17152: b"\x00\x17\nC\x00", 14081: b"\x00;\x0b7\x00"},
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-52,
    service_data={},
    source="local",
)

TP970R = make_bluetooth_service_info(
    name="TP970R",
    manufacturer_data={13568: b"\x00F\x0b5\x00"},
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-75,
    service_data={},
    source="local",
)
TP970R_2 = make_bluetooth_service_info(
    name="TP970R",
    manufacturer_data={13312: b"\x00\xae\x0b4\x00"},
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-75,
    service_data={},
    source="local",
)

TP972S = make_bluetooth_service_info(
    name="TP972S",
    manufacturer_data={29184: b"\x00j\n3\xd3\xb8B\x00@\xaeBf\x06\xaeBlTswD\xf8"},
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-75,
    service_data={},
    source="local",
)
TP972S_2 = make_bluetooth_service_info(
    name="TP972S",
    manufacturer_data={36096: b"\x00\xa6\n\xcd\xec\xffB\x9ai\x00C\x9ai\x00ClTswD\xf8"},
    service_uuids=["72fbb631-6f6b-d1ba-db55-2ee6fdd942bd"],
    address="aa:bb:cc:dd:ee:ff",
    rssi=-75,
    service_data={},
    source="local",
)

TP357S_UPDATE_1 = make_bluetooth_service_info(
    name="TP357S (C890)",
    address="C3:18:C9:9C:C8:90",
    rssi=-57,
    manufacturer_data={
        51138: b'\x00\x14"\x0b\x01',
        50882: b'\x00\x14"\x0b\x01',
        51394: b'\x00\x14"\x0b\x01',
        51650: b'\x00\x14"\x0b\x01',
        50626: b'\x00\x14"\x0b\x01',
        50370: b'\x00\x14"\x0b\x01',
        51906: b'\x00\x14"\x0b\x01',
        50114: b'\x00\x14"\x0b\x01',
        52162: b'\x00\x14"\x0b\x01',
        52418: b'\x00\x14"\x0b\x01',
        52674: b'\x00\x14"\x0b\x01',
        49858: b'\x00\x14"\x0b\x01',
        52930: b'\x00\x14"\x0b\x01',
        53442: b'\x00\x19"\x0b\x01',
        53698: b'\x00\x14"\x0b\x01',
        53954: b'\x00\x14"\x0b\x01',
        54210: b'\x00\x14"\x0b\x01',
        54466: b'\x00\x14"\x0b\x01',
        54722: b'\x00\x14"\x0b\x01',
        54978: b'\x00\x14"\x0b\x01',
    },
    service_data={},
    service_uuids=[],
    source="2C:CF:67:1B:03:3A",
)
TP357S_UPDATE_2 = make_bluetooth_service_info(
    name="TP357S (C890)",
    address="C3:18:C9:9C:C8:90",
    rssi=-56,
    manufacturer_data={
        51138: b'\x00\x14"\x0b\x01',
        50882: b'\x00\x14"\x0b\x01',
        51394: b'\x00\x14"\x0b\x01',
        51650: b'\x00\x14"\x0b\x01',
        50626: b'\x00\x14"\x0b\x01',
        50370: b'\x00\x14"\x0b\x01',
        51906: b'\x00\x14"\x0b\x01',
        50114: b'\x00\x14"\x0b\x01',
        52162: b'\x00\x14"\x0b\x01',
        52418: b'\x00\x14"\x0b\x01',
        52674: b'\x00\x14"\x0b\x01',
        49858: b'\x00\x14"\x0b\x01',
        52930: b'\x00\x14"\x0b\x01',
        53442: b'\x00\x14"\x0b\x01',
        53698: b'\x00\x14"\x0b\x01',
        53954: b'\x00\x14"\x0b\x01',
        54210: b'\x00\x14"\x0b\x01',
        54466: b'\x00\x14"\x0b\x01',
        54722: b'\x00\x14"\x0b\x01',
        54978: b'\x00\x14"\x0b\x01',
    },
    service_data={},
    service_uuids=[],
    source="2C:CF:67:1B:03:3A",
)
TP357S_UPDATE_3 = make_bluetooth_service_info(
    name="TP357S (C890)",
    address="C3:18:C9:9C:C8:90",
    rssi=-65,
    manufacturer_data={
        51138: b'\x00\x14"\x0b\x01',
        50882: b'\x00\x14"\x0b\x01',
        51394: b'\x00\x14"\x0b\x01',
        51650: b'\x00\x14"\x0b\x01',
        50626: b'\x00\x14"\x0b\x01',
        50370: b'\x00\x14"\x0b\x01',
        51906: b'\x00\x14"\x0b\x01',
        50114: b'\x00\x14"\x0b\x01',
        52162: b'\x00\x14"\x0b\x01',
        52418: b'\x00\x14"\x0b\x01',
        52674: b'\x00\x14"\x0b\x01',
        49858: b'\x00\x14"\x0b\x01',
        52930: b'\x00\x14"\x0b\x01',
        53442: b'\x00\x14"\x0b\x01',
        53698: b'\x00\x14"\x0b\x01',
        53954: b'\x00\x14"\x0b\x01',
        54210: b'\x00\x14"\x0b\x01',
        54466: b'\x00\x14"\x0b\x01',
        54722: b'\x00\x14"\x0b\x01',
        54978: b'\x00\x14"\x0b\x01',
        53186: b'\x00\x14"\x0b\x01',
    },
    service_data={},
    service_uuids=[],
    source="2C:CF:67:1B:03:3A",
)
TP357S_UPDATE_4 = make_bluetooth_service_info(
    name="TP357S (C890)",
    address="C3:18:C9:9C:C8:90",
    rssi=-55,
    manufacturer_data={
        51138: b'\x00\x14"\x0b\x01',
        50882: b'\x00\x14"\x0b\x01',
        51394: b'\x00\n"\x0b\x01',
        51650: b'\x00\x14"\x0b\x01',
        50626: b'\x00\x14"\x0b\x01',
        50370: b'\x00\x14"\x0b\x01',
        51906: b'\x00\x14"\x0b\x01',
        50114: b'\x00\x14"\x0b\x01',
        52162: b'\x00\x14"\x0b\x01',
        52418: b'\x00\x14"\x0b\x01',
        52674: b'\x00\x14"\x0b\x01',
        49858: b'\x00\x14"\x0b\x01',
        52930: b'\x00\x14"\x0b\x01',
        53442: b'\x00\x14"\x0b\x01',
        53698: b'\x00\x14"\x0b\x01',
        53954: b'\x00\x14"\x0b\x01',
        54210: b'\x00\x14"\x0b\x01',
        54466: b'\x00\x14"\x0b\x01',
        54722: b'\x00\x14"\x0b\x01',
        54978: b'\x00\x14"\x0b\x01',
        53186: b'\x00\x14"\x0b\x01',
    },
    service_data={},
    service_uuids=[],
    source="2C:CF:67:1B:03:3A",
)

INVALID_TP972 = make_bluetooth_service_info(
    name="TP972S",
    address="C3:18:C9:9C:C8:90",
    rssi=-55,
    manufacturer_data={
        51138: b"\x01\x8d\x00\xe1\n3\x13\xfaB\x00\xc0\xfaB\x9a\xf9\xfaBlTswD\xf8"
    },
    service_data={},
    service_uuids=[],
    source="2C:CF:67:1B:03:3A",
)

# Nonexistent (at time of writing) device
INVALID_DEVICE = make_bluetooth_service_info(
    name="TP9000NOTHING",
    address="C3:18:C9:9C:C8:90",
    rssi=-55,
    manufacturer_data={
        51138: b"\x01\x8d\x00\xe1\n3\x13\xfaB\x00\xc0\xfaB\x9a\xf9\xfaBlTswD\xf8"
    },
    service_data={},
    service_uuids=[],
    source="2C:CF:67:1B:03:3A",
)


def test_supported_set_the_title():
    parser = ThermoProBluetoothDeviceData()
    assert parser.supported(TP357) is True
    assert parser.title == "TP357 (2142) EEFF"


def test_tp357():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP357) == SensorUpdate(
        title="TP357 (2142) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP357 (2142)",
                model="TP357",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24.1,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=29,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )


def test_tp357_raw():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP357_RAW) == SensorUpdate(
        title="TP357 (2142) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP357 (2142)",
                model="TP357",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24.1,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=29,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )


def test_tp960r():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP960R) == SensorUpdate(
        title="TP960R (0000) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP960R (0000)",
                model="TP960R",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(
                key="internal_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="ambient_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="battery_probe_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="internal_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Temperature",
                native_value=28,
            ),
            DeviceKey(key="ambient_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                name="Probe 1 Ambient Temperature",
                native_value=26,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-75,
            ),
            DeviceKey(key="battery_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                name="Probe 1 Battery",
                native_value=9,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )
    assert parser.update(TP960R_2) == SensorUpdate(
        title="TP960R (0000) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP960R (0000)",
                model="TP960R",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(
                key="internal_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="ambient_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="battery_probe_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="internal_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Temperature",
                native_value=28,
            ),
            DeviceKey(key="ambient_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                name="Probe 1 Ambient Temperature",
                native_value=26,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-75,
            ),
            DeviceKey(key="battery_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                name="Probe 1 Battery",
                native_value=9,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )


def test_tp962r():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP962R) == SensorUpdate(
        title="TP962R (0000) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP962R (0000)",
                model="TP962R",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(
                key="internal_temperature_probe_2", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_temperature_probe_2", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="ambient_temperature_probe_2", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_2", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="battery_probe_2", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_2", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="internal_temperature_probe_2", device_id=None): SensorValue(
                device_key=DeviceKey(
                    key="internal_temperature_probe_2", device_id=None
                ),
                name="Probe 2 Internal Temperature",
                native_value=25,
            ),
            DeviceKey(key="ambient_temperature_probe_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_2", device_id=None),
                name="Probe 2 Ambient Temperature",
                native_value=25,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-52,
            ),
            DeviceKey(key="battery_probe_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_2", device_id=None),
                name="Probe 2 Battery",
                native_value=100.0,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )
    assert parser.update(TP962R_2) == SensorUpdate(
        title="TP962R (0000) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP962R (0000)",
                model="TP962R",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(
                key="ambient_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="internal_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(
                key="ambient_temperature_probe_2", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_2", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery_probe_2", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_2", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="battery_probe_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(
                key="internal_temperature_probe_2", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_temperature_probe_2", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
        },
        entity_values={
            DeviceKey(key="ambient_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                name="Probe 1 Ambient Temperature",
                native_value=37,
            ),
            DeviceKey(key="internal_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Temperature",
                native_value=37,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-52,
            ),
            DeviceKey(key="ambient_temperature_probe_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_2", device_id=None),
                name="Probe 2 Ambient Temperature",
                native_value=25,
            ),
            DeviceKey(key="battery_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                name="Probe 1 Battery",
                native_value=82,
            ),
            DeviceKey(key="battery_probe_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_2", device_id=None),
                name="Probe 2 Battery",
                native_value=100.0,
            ),
            DeviceKey(key="internal_temperature_probe_2", device_id=None): SensorValue(
                device_key=DeviceKey(
                    key="internal_temperature_probe_2", device_id=None
                ),
                name="Probe 2 Internal Temperature",
                native_value=25,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )


def test_tp357s():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP357_S) == SensorUpdate(
        title="TP357S (2142) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP357S (2142)",
                model="TP357S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=23.8,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=41,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )
    assert parser.update(TP357_S_2) == SensorUpdate(
        title="TP357S (2142) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP357S (2142)",
                model="TP357S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=23.8,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=41,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )


def test_tp357_add():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP357_ADD) == SensorUpdate(
        title="TP357 (2142) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP357 (2142)",
                model="TP357",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24.9,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=16,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )


def test_tp393():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP393) == SensorUpdate(
        title="TP393 (9376) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP393 (9376)",
                model="TP393",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24.2,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=53,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )


def test_tp393_multi_updates():
    parser = ThermoProBluetoothDeviceData()
    assert parser.supported(TP393_DETECT_CHANGED_1) is True
    parser.update(TP393_DETECT_CHANGED_1)
    result = parser.update(TP393_DETECT_CHANGED_2)
    assert result == SensorUpdate(
        title="TP393 (9376) EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP393 (9376)",
                model="TP393",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            )
        },
        entity_values={
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            )
        },
        binary_entity_descriptions={},
        binary_entity_values={},
    )


def test_tp970r():
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP970R) == SensorUpdate(
        title="TP970R EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP970R",
                model="TP970R",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_probe_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(
                key="internal_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="ambient_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
        },
        entity_values={
            DeviceKey(key="battery_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                name="Probe 1 Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-75,
            ),
            DeviceKey(key="internal_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Temperature",
                native_value=23,
            ),
            DeviceKey(key="ambient_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                name="Probe 1 Ambient Temperature",
                native_value=23,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )
    assert parser.update(TP970R_2) == SensorUpdate(
        title="TP970R EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP970R",
                model="TP970R",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_probe_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(
                key="internal_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="ambient_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
        },
        entity_values={
            DeviceKey(key="battery_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                name="Probe 1 Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-75,
            ),
            DeviceKey(key="internal_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(
                    key="internal_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Temperature",
                native_value=22,
            ),
            DeviceKey(key="ambient_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                name="Probe 1 Ambient Temperature",
                native_value=22,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )


def test_tp972s() -> None:
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(TP972S) == SensorUpdate(
        title="TP972S EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP972S",
                model="TP972S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_probe_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(
                key="internal_tip_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_tip_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="internal_center_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_center_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="internal_end_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_end_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="ambient_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
        },
        entity_values={
            DeviceKey(key="battery_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                name="Probe 1 Battery",
                native_value=90.0,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-75,
            ),
            DeviceKey(
                key="internal_tip_temperature_probe_1", device_id=None
            ): SensorValue(
                device_key=DeviceKey(
                    key="internal_tip_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Tip Temperature",
                native_value=3.6,
            ),
            DeviceKey(
                key="internal_center_temperature_probe_1", device_id=None
            ): SensorValue(
                device_key=DeviceKey(
                    key="internal_center_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Center Temperature",
                native_value=0.6,
            ),
            DeviceKey(
                key="internal_end_temperature_probe_1", device_id=None
            ): SensorValue(
                device_key=DeviceKey(
                    key="internal_end_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal End Temperature",
                native_value=0.6,
            ),
            DeviceKey(key="ambient_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                name="Probe 1 Ambient Temperature",
                native_value=15,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )
    assert parser.update(TP972S_2) == SensorUpdate(
        title="TP972S EEFF",
        devices={
            None: SensorDeviceInfo(
                name="TP972S",
                model="TP972S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_probe_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(
                key="internal_tip_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_tip_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="internal_center_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_center_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="internal_end_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(
                    key="internal_end_temperature_probe_1", device_id=None
                ),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(
                key="ambient_temperature_probe_1", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
        },
        entity_values={
            DeviceKey(key="battery_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_probe_1", device_id=None),
                name="Probe 1 Battery",
                native_value=95.0,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-75,
            ),
            DeviceKey(
                key="internal_tip_temperature_probe_1", device_id=None
            ): SensorValue(
                device_key=DeviceKey(
                    key="internal_tip_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Tip Temperature",
                native_value=23.3,
            ),
            DeviceKey(
                key="internal_center_temperature_probe_1", device_id=None
            ): SensorValue(
                device_key=DeviceKey(
                    key="internal_center_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal Center Temperature",
                native_value=23.6,
            ),
            DeviceKey(
                key="internal_end_temperature_probe_1", device_id=None
            ): SensorValue(
                device_key=DeviceKey(
                    key="internal_end_temperature_probe_1", device_id=None
                ),
                name="Probe 1 Internal End Temperature",
                native_value=23.6,
            ),
            DeviceKey(key="ambient_temperature_probe_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="ambient_temperature_probe_1", device_id=None),
                name="Probe 1 Ambient Temperature",
                native_value=30.0,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )


def test_tp357s_four_updates():
    parser = ThermoProBluetoothDeviceData()

    assert parser.update(TP357S_UPDATE_1) == SensorUpdate(
        title="TP357S (C890) C890",
        devices={
            None: SensorDeviceInfo(
                name="TP357S (C890)",
                model="TP357S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            )
        },
        entity_values={
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-57,
            )
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )

    assert parser.update(TP357S_UPDATE_2) == SensorUpdate(
        title="TP357S (C890) C890",
        devices={
            None: SensorDeviceInfo(
                name="TP357S (C890)",
                model="TP357S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-56,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=20.8,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=20,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )
    assert parser.update(TP357S_UPDATE_3) == SensorUpdate(
        title="TP357S (C890) C890",
        devices={
            None: SensorDeviceInfo(
                name="TP357S (C890)",
                model="TP357S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-65,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=20.7,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=20,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )
    assert parser.update(TP357S_UPDATE_4) == SensorUpdate(
        title="TP357S (C890) C890",
        devices={
            None: SensorDeviceInfo(
                name="TP357S (C890)",
                model="TP357S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
        },
        entity_values={
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-55,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=20.0,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=10,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )


def test_parser_error_1() -> None:
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(INVALID_TP972) == SensorUpdate(
        title="TP972S C890",
        devices={
            None: SensorDeviceInfo(
                name="TP972S",
                model="TP972S",
                manufacturer="ThermoPro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-55,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )


def test_parser_error_2() -> None:
    parser = ThermoProBluetoothDeviceData()
    assert parser.update(INVALID_DEVICE) == SensorUpdate(
        title=None,
        devices={},
        entity_descriptions={},
        entity_values={},
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )

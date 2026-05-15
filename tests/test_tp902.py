"""Tests for the TP902 / TP920 protocol helpers."""

from __future__ import annotations

import pytest

from thermopro_ble.tp902 import (
    ALARM_OFF,
    ALARM_RANGE,
    ALARM_TARGET,
    AUTH_PACKET,
    CMD_GET_ALARM,
    CMD_SET_ALARM,
    CMD_SET_SOUND,
    CMD_SET_UNITS,
    CMD_TIME_SYNC,
    PROBE_COUNT,
    SOUND_OFF,
    SOUND_ON,
    UNITS_C,
    UNITS_F,
    AlarmConfig,
    AuthResponse,
    DeviceStatus,
    FirmwareVersion,
    TemperatureBroadcast,
    TemperatureSnapshot,
    UnknownFrame,
    build_auth_packet,
    build_get_alarm,
    build_packet,
    build_set_alarm,
    build_set_sound,
    build_set_units,
    build_time_sync,
    decode_temp_bcd,
    encode_temp_bcd,
    parse_notification,
    supports,
    verify_checksum,
)


class TestBcd:
    def test_decode_positive(self):
        # 0x0999 → 99.9 °C (captured TP902 broadcast probe 1)
        assert decode_temp_bcd(b"\x09\x99") == 99.9

    def test_decode_three_digits(self):
        # 0x1007 → 100.7 °C (captured TP902 broadcast probe 2)
        assert decode_temp_bcd(b"\x10\x07") == 100.7

    def test_decode_empty_probe(self):
        assert decode_temp_bcd(b"\xff\xff") is None

    def test_decode_negative(self):
        # High bit of byte 0 means negative; remaining nibbles decode normally.
        assert decode_temp_bcd(b"\x82\x55") == pytest.approx(-25.5)

    def test_decode_zero(self):
        assert decode_temp_bcd(b"\x00\x00") == 0.0

    def test_decode_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            decode_temp_bcd(b"\x09")

    @pytest.mark.parametrize(
        "value,expected",
        [
            (99.9, b"\x09\x99"),
            (100.7, b"\x10\x07"),
            (0.0, b"\x00\x00"),
            (25.5, b"\x02\x55"),
        ],
    )
    def test_encode_round_trip(self, value, expected):
        assert encode_temp_bcd(value) == expected
        assert decode_temp_bcd(expected) == pytest.approx(value)

    def test_encode_negative(self):
        encoded = encode_temp_bcd(-25.5)
        assert encoded == b"\x82\x55"
        assert decode_temp_bcd(encoded) == pytest.approx(-25.5)

    def test_encode_none_yields_empty_probe(self):
        assert encode_temp_bcd(None) == b"\xff\xff"

    def test_encode_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            encode_temp_bcd(1000.0)
        with pytest.raises(ValueError):
            encode_temp_bcd(-1000.0)


class TestPacket:
    def test_build_basic_frame(self):
        # cmd=0x24 len=1 data=01 → checksum = (0x24+0x01+0x01)&0xff = 0x26
        assert build_packet(0x24, b"\x01") == b"\x24\x01\x01\x26"

    def test_build_empty_payload(self):
        # cmd=0x26 len=0 → checksum = 0x26
        assert build_packet(0x26) == b"\x26\x00\x26"

    def test_build_rejects_invalid_cmd(self):
        with pytest.raises(ValueError):
            build_packet(0x100)
        with pytest.raises(ValueError):
            build_packet(-1)

    def test_build_rejects_oversized_payload(self):
        with pytest.raises(ValueError):
            build_packet(0x24, b"\x00" * 256)

    def test_verify_checksum_round_trip(self):
        frame = build_packet(0x24, b"\x01")
        assert verify_checksum(frame) is True

    def test_verify_checksum_rejects_truncated(self):
        assert verify_checksum(b"\x24") is False
        assert verify_checksum(b"\x24\x01") is False  # missing data + cs

    def test_verify_checksum_rejects_bad_checksum(self):
        assert verify_checksum(b"\x24\x01\x01\x00") is False

    def test_verify_checksum_tolerates_padding(self):
        # Notifications are typically 20 bytes; bytes past the checksum are
        # padding and must not affect verification.
        frame = build_packet(0x24, b"\x01") + b"\x00" * 10
        assert verify_checksum(frame) is True


class TestParseNotification:
    def test_temperature_broadcast(self):
        # Captured TP902 broadcast (from issue #152):
        # cmd=0x30 len=0x0f bat=0x4c units=C alarms=0
        # probes: 99.9 / 100.7 / -- / -- / -- / --
        # checksum 0x48 then 0x01 0x20 padding.
        raw = bytes.fromhex("300f4c0c0009991007ffffffffffffffff480120")
        parsed = parse_notification(raw)
        assert isinstance(parsed, TemperatureBroadcast)
        assert parsed.battery == 0x4C  # 76 %
        assert parsed.units == "C"
        assert parsed.alarms == 0
        assert parsed.temperatures == (99.9, 100.7, None, None, None, None)
        assert len(parsed.temperatures) == PROBE_COUNT

    def test_temperature_broadcast_fahrenheit(self):
        # Same shape, units byte flipped to 0x0f.
        payload = bytes([0x4C, UNITS_F, 0x00]) + b"\x09\x99" + b"\xff\xff" * 5
        frame = build_packet(0x30, payload)
        parsed = parse_notification(frame)
        assert isinstance(parsed, TemperatureBroadcast)
        assert parsed.units == "F"
        assert parsed.temperatures[0] == 99.9

    def test_device_status(self):
        # 0x26 status: units=C, beeper ON, battery=80
        frame = build_packet(0x26, bytes([UNITS_C, SOUND_ON, 80, 0x00, 0x00]))
        parsed = parse_notification(frame)
        assert isinstance(parsed, DeviceStatus)
        assert parsed.units == "C"
        assert parsed.beeper_on is True
        assert parsed.battery == 80

    def test_device_status_beeper_off(self):
        frame = build_packet(0x26, bytes([UNITS_F, SOUND_OFF, 42, 0x00, 0x00]))
        parsed = parse_notification(frame)
        assert isinstance(parsed, DeviceStatus)
        assert parsed.units == "F"
        assert parsed.beeper_on is False
        assert parsed.battery == 42

    def test_alarm_range(self):
        # Issue #152 capture: ch1 RANGE lo=80.9°C hi=119.7°C
        raw = bytes.fromhex("2406018211970809660000000000510f0400392e")
        parsed = parse_notification(raw)
        assert isinstance(parsed, AlarmConfig)
        assert parsed.channel == 1
        assert parsed.mode == ALARM_RANGE
        # value1 = 119.7 (hi), value2 = 80.9 (lo); both BCD-encoded.
        assert parsed.value1 == pytest.approx(119.7)
        assert parsed.value2 == pytest.approx(80.9)

    def test_alarm_target(self):
        # Issue #152 capture: ch2 TARGET=74.0°C
        raw = bytes.fromhex("2406020a074000007d0000000000510f0400be3a")
        parsed = parse_notification(raw)
        assert isinstance(parsed, AlarmConfig)
        assert parsed.channel == 2
        assert parsed.mode == ALARM_TARGET
        assert parsed.value1 == pytest.approx(74.0)

    def test_firmware_version(self):
        frame = build_packet(0x41, bytes([0x12]))
        parsed = parse_notification(frame)
        assert isinstance(parsed, FirmwareVersion)
        assert parsed.major == 1
        assert parsed.minor == 2

    def test_auth_response(self):
        frame = build_packet(0x01, b"\xab\xcd")
        parsed = parse_notification(frame)
        assert isinstance(parsed, AuthResponse)
        assert parsed.data == b"\xab\xcd"

    def test_temperature_snapshot(self):
        # 0x25 snapshot: probe_count=6, alarms=0, all probes at 50.0°C
        body = bytes([6, 0]) + encode_temp_bcd(50.0) * PROBE_COUNT
        frame = build_packet(0x25, body)
        parsed = parse_notification(frame)
        assert isinstance(parsed, TemperatureSnapshot)
        assert parsed.probe_count == 6
        assert parsed.temperatures == (50.0,) * PROBE_COUNT

    def test_unknown_cmd_is_preserved(self):
        frame = build_packet(0x7E, b"\xde\xad\xbe\xef")
        parsed = parse_notification(frame)
        assert isinstance(parsed, UnknownFrame)
        assert parsed.cmd == 0x7E
        assert parsed.data == b"\xde\xad\xbe\xef"

    def test_too_short(self):
        assert parse_notification(b"\x30") is None

    def test_bad_checksum(self):
        # Build a valid frame, then flip the checksum byte.
        frame = bytearray(build_packet(0x26))
        frame[-1] ^= 0xFF
        assert parse_notification(bytes(frame)) is None


class TestBuilders:
    def test_auth_packet_constant(self):
        # Auth handshake is a fixed captured payload.
        assert build_auth_packet() == AUTH_PACKET
        assert len(AUTH_PACKET) == 12

    def test_set_units_celsius(self):
        frame = build_set_units(celsius=True)
        assert frame[0] == CMD_SET_UNITS
        assert frame[2] == UNITS_C
        assert verify_checksum(frame)

    def test_set_units_fahrenheit(self):
        frame = build_set_units(celsius=False)
        assert frame[2] == UNITS_F

    def test_set_sound(self):
        on = build_set_sound(True)
        off = build_set_sound(False)
        assert on[0] == CMD_SET_SOUND and on[2] == SOUND_ON
        assert off[2] == SOUND_OFF

    def test_get_alarm_channel_validation(self):
        assert build_get_alarm(1)[0] == CMD_GET_ALARM
        with pytest.raises(ValueError):
            build_get_alarm(0)
        with pytest.raises(ValueError):
            build_get_alarm(PROBE_COUNT + 1)

    def test_set_alarm_off(self):
        frame = build_set_alarm(1, ALARM_OFF)
        assert frame[0] == CMD_SET_ALARM
        # body: channel, mode, ff ff 00 00? - actually for OFF both are ff ff
        body = frame[2:-1]
        assert body[0] == 1
        assert body[1] == ALARM_OFF
        assert body[2:] == b"\xff\xff\xff\xff"

    def test_set_alarm_target_requires_value(self):
        with pytest.raises(ValueError):
            build_set_alarm(1, ALARM_TARGET)

    def test_set_alarm_target(self):
        frame = build_set_alarm(2, ALARM_TARGET, value1=74.0)
        body = frame[2:-1]
        assert body[0] == 2
        assert body[1] == ALARM_TARGET
        assert decode_temp_bcd(body[2:4]) == pytest.approx(74.0)
        assert body[4:] == b"\x00\x00"

    def test_set_alarm_range(self):
        frame = build_set_alarm(1, ALARM_RANGE, value1=119.7, value2=80.9)
        body = frame[2:-1]
        assert body[0] == 1
        assert body[1] == ALARM_RANGE
        assert decode_temp_bcd(body[2:4]) == pytest.approx(119.7)
        assert decode_temp_bcd(body[4:6]) == pytest.approx(80.9)

    def test_set_alarm_range_requires_both_values(self):
        with pytest.raises(ValueError):
            build_set_alarm(1, ALARM_RANGE, value1=119.7)
        with pytest.raises(ValueError):
            build_set_alarm(1, ALARM_RANGE, value2=80.9)

    def test_set_alarm_rejects_unknown_mode(self):
        with pytest.raises(ValueError):
            build_set_alarm(1, 0x77)

    def test_set_alarm_rejects_bad_channel(self):
        with pytest.raises(ValueError):
            build_set_alarm(0, ALARM_OFF)
        with pytest.raises(ValueError):
            build_set_alarm(PROBE_COUNT + 1, ALARM_OFF)

    def test_time_sync(self):
        frame = build_time_sync(0)
        assert frame[0] == CMD_TIME_SYNC
        # 4-byte LE payload
        assert frame[2:6] == b"\x00\x00\x00\x00"
        assert verify_checksum(frame)

    def test_time_sync_range(self):
        with pytest.raises(ValueError):
            build_time_sync(-1)
        with pytest.raises(ValueError):
            build_time_sync(1 << 32)


class TestSupports:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("TP902", True),
            ("TP920", True),
            ("TP902 (2142)", True),
            ("TP920 (abc)", True),
            ("TP357", False),
            ("TP358S", False),
            ("", False),
            ("TP9", False),
        ],
    )
    def test_supports(self, name, expected):
        assert supports(name) is expected

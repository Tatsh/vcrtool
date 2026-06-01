from __future__ import annotations

from typing import TYPE_CHECKING

from vcrtool.sansio import (
    FRAME_DURATION_US,
    ONE_MARK_US,
    SPACE_US,
    START_MARK_US,
    ZERO_MARK_US,
    CommandStatus,
    JLIPCodec,
    Pulse,
    SIRCSCodec,
    SIRCSCommand,
    SIRCSVariant,
    checksum,
)
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def codec() -> SIRCSCodec:
    """Fixture for a SIRCS codec."""
    return SIRCSCodec()


@pytest.fixture
def jlip_codec() -> JLIPCodec:
    """Fixture for a JLIP codec."""
    return JLIPCodec()


@pytest.mark.parametrize(('variant', 'expected_bits'), [
    (SIRCSVariant.TWELVE_BIT, 12),
    (SIRCSVariant.FIFTEEN_BIT, 15),
    (SIRCSVariant.TWENTY_BIT, 20),
])
def test_variant_total_bits(variant: SIRCSVariant, expected_bits: int) -> None:
    assert variant.total_bits == expected_bits
    assert variant.command_bits == 7
    assert variant.command_bits + variant.address_bits + variant.extended_bits == expected_bits


def test_encode_starts_with_header(codec: SIRCSCodec) -> None:
    pulses = codec.encode(SIRCSCommand(command=0, address=0))
    assert pulses[0] == Pulse(carrier_on=True, duration_us=START_MARK_US)
    assert pulses[1] == Pulse(carrier_on=False, duration_us=SPACE_US)


def test_encode_marks_match_bits(codec: SIRCSCodec) -> None:
    marks = [
        pulse.duration_us for pulse in codec.encode(SIRCSCommand(command=1, address=0))
        if pulse.carrier_on
    ]
    assert marks[0] == START_MARK_US
    assert marks[1] == ONE_MARK_US
    assert all(mark == ZERO_MARK_US for mark in marks[2:])


def test_encode_frame_is_padded_to_full_period(codec: SIRCSCodec) -> None:
    pulses = codec.encode(SIRCSCommand(command=0, address=0))
    assert sum(pulse.duration_us for pulse in pulses) == FRAME_DURATION_US


def test_encode_lsb_first_order(codec: SIRCSCodec) -> None:
    marks = [
        pulse.duration_us for pulse in codec.encode(SIRCSCommand(command=0b0000001, address=0))
        if pulse.carrier_on
    ]
    assert marks[1] == ONE_MARK_US
    assert marks[2] == ZERO_MARK_US


def test_encode_repeat_concatenates_frames(codec: SIRCSCodec) -> None:
    single = codec.encode(SIRCSCommand(command=5, address=3))
    repeated = codec.encode(SIRCSCommand(command=5, address=3), repeat=3)
    assert len(repeated) == len(single) * 3
    assert repeated == single * 3


@pytest.mark.parametrize('repeat', [0, -1])
def test_encode_rejects_non_positive_repeat(codec: SIRCSCodec, repeat: int) -> None:
    with pytest.raises(ValueError, match='repeat must be at least 1'):
        codec.encode(SIRCSCommand(command=0, address=0), repeat=repeat)


@pytest.mark.parametrize(('command', 'match'), [
    (SIRCSCommand(command=128, address=0), 'command value 128'),
    (SIRCSCommand(command=0, address=32), 'address value 32'),
    (SIRCSCommand(command=-1, address=0), 'command value -1'),
])
def test_encode_rejects_out_of_range_fields(codec: SIRCSCodec, command: SIRCSCommand,
                                            match: str) -> None:
    with pytest.raises(ValueError, match=match):
        codec.encode(command)


@pytest.mark.parametrize('variant', list(SIRCSVariant))
def test_encode_then_decode_round_trip(codec: SIRCSCodec, variant: SIRCSVariant) -> None:
    original = SIRCSCommand(command=0b1010101,
                            address=(1 << variant.address_bits) - 1,
                            extended=(1 << variant.extended_bits) - 1,
                            variant=variant)
    assert codec.decode(codec.encode(original)) == original


def test_decode_tolerates_jitter(codec: SIRCSCodec) -> None:
    pulses = [
        Pulse(carrier_on=p.carrier_on, duration_us=p.duration_us + 60) if p.carrier_on else p
        for p in codec.encode(SIRCSCommand(command=42, address=7))
    ]
    assert codec.decode(pulses) == SIRCSCommand(command=42, address=7)


def test_decode_ignores_trailing_repeat(codec: SIRCSCodec) -> None:
    pulses = codec.encode(SIRCSCommand(command=9, address=4), repeat=3)
    assert codec.decode(pulses) == SIRCSCommand(command=9, address=4)


def test_decode_rejects_missing_start(codec: SIRCSCodec) -> None:
    with pytest.raises(ValueError, match='does not begin with a start mark'):
        codec.decode([Pulse(carrier_on=True, duration_us=ONE_MARK_US)])


def test_decode_rejects_empty(codec: SIRCSCodec) -> None:
    with pytest.raises(ValueError, match='does not begin with a start mark'):
        codec.decode([])


def test_decode_rejects_unknown_mark(codec: SIRCSCodec) -> None:
    pulses = [
        Pulse(carrier_on=True, duration_us=START_MARK_US),
        Pulse(carrier_on=False, duration_us=SPACE_US),
        Pulse(carrier_on=True, duration_us=99)
    ]
    with pytest.raises(ValueError, match='matches neither a zero nor a one'):
        codec.decode(pulses)


def test_decode_rejects_unknown_variant(codec: SIRCSCodec) -> None:
    pulses = [Pulse(carrier_on=True, duration_us=START_MARK_US)]
    pulses.extend(Pulse(carrier_on=True, duration_us=ZERO_MARK_US) for _ in range(3))
    with pytest.raises(ValueError, match='do not correspond to a known SIRCS variant'):
        codec.decode(pulses)


@pytest.mark.parametrize(('vals', 'expected'), [
    ([0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0],
     (0x80 - sum(v & 0x7F
                 for v in [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0])) & 0x7F),
    ([0] * 10, 0x80 & 0x7F),
    ([0xFF] * 10, (0x80 - sum(0xFF & 0x7F for _ in range(10))) & 0x7F),
])
def test_checksum(vals: list[int], expected: int) -> None:
    assert checksum(vals) == expected


def test_build_command_frames_bytes(jlip_codec: JLIPCodec) -> None:
    frame = jlip_codec.build_command(1, 0x01, 0x02, 0x03)
    assert frame == bytes(
        [255, 255, 1, 1, 2, 3, 0, 0, 0, 0,
         checksum([255, 255, 1, 1, 2, 3, 0, 0, 0, 0])])


def test_validate_response_returns_data(jlip_codec: JLIPCodec, mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.sansio.checksum', return_value=0x7C)
    data = b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C'
    assert jlip_codec.validate_response(data) == data


def test_validate_response_rejects_bad_checksum(jlip_codec: JLIPCodec,
                                                mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.sansio.checksum', return_value=0x7C)
    with pytest.raises(ValueError, match='Checksum did not match'):
        jlip_codec.validate_response(b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7D')


def test_validate_response_rejects_bad_status(jlip_codec: JLIPCodec, mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.sansio.checksum', return_value=0x7C)
    with pytest.raises(ValueError, match='Command status'):
        jlip_codec.validate_response(b'\xFF\xFF\x01\x05\x00\x00\x00\x00\x00\x00\x7C')


def test_validate_response_status_not_raised(jlip_codec: JLIPCodec, mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.sansio.checksum', return_value=0x7C)
    data = b'\xFF\xFF\x01\x05\x00\x00\x00\x00\x00\x00\x7C'
    assert jlip_codec.validate_response(data, raise_on_error=False) == data
    assert CommandStatus(data[3] & 0b111) == CommandStatus.COMMAND_NOT_POSSIBLE

from __future__ import annotations

from typing import TYPE_CHECKING

from vcrtool.sansio import Pulse, SIRCSCommand
from vcrtool.sircs import PicoSIRCSTransport
import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytest_mock import MockerFixture


def test_serialize_basic() -> None:
    pulses = [Pulse(carrier_on=True, duration_us=600), Pulse(carrier_on=False, duration_us=600)]
    assert PicoSIRCSTransport.serialize(pulses) == bytes([0xA5, 0, 2, 1, 2, 88, 0, 2, 88])


def test_serialize_invert() -> None:
    pulses = [Pulse(carrier_on=True, duration_us=600), Pulse(carrier_on=False, duration_us=600)]
    assert PicoSIRCSTransport.serialize(pulses,
                                        invert=True) == bytes([0xA5, 0, 2, 0, 2, 88, 1, 2, 88])


def test_serialize_rejects_long_duration() -> None:
    with pytest.raises(ValueError, match='does not fit in 16 bits'):
        PicoSIRCSTransport.serialize([Pulse(carrier_on=True, duration_us=70_000)])


def test_serialize_rejects_too_many_pulses() -> None:
    def pulses() -> Iterator[Pulse]:
        for _ in range(0x10000 + 1):
            yield Pulse(carrier_on=True, duration_us=0)

    with pytest.raises(ValueError, match='Too many pulses to serialise'):
        PicoSIRCSTransport.serialize(pulses())


def test_transmit_writes_serialized(mocker: MockerFixture) -> None:
    mock_serial = mocker.patch('serial.Serial')
    pico = PicoSIRCSTransport('/dev/ttyACM0')
    pulses = [Pulse(carrier_on=True, duration_us=600), Pulse(carrier_on=False, duration_us=600)]
    pico.transmit(pulses)
    mock_serial.return_value.write.assert_called_once_with(PicoSIRCSTransport.serialize(pulses))


def test_transmit_applies_invert(mocker: MockerFixture) -> None:
    mock_serial = mocker.patch('serial.Serial')
    pico = PicoSIRCSTransport('/dev/ttyACM0', invert=True)
    pulses = [Pulse(carrier_on=True, duration_us=600)]
    pico.transmit(pulses)
    mock_serial.return_value.write.assert_called_once_with(
        PicoSIRCSTransport.serialize(pulses, invert=True))


def test_send_command_writes_frame(mocker: MockerFixture) -> None:
    mock_serial = mocker.patch('serial.Serial')
    pico = PicoSIRCSTransport('/dev/ttyACM0')
    pico.send_command(SIRCSCommand(command=1, address=1), repeat=1)
    mock_serial.return_value.write.assert_called_once()
    buffer = mock_serial.return_value.write.call_args.args[0]
    assert buffer[0] == 0xA5
    # A twelve-bit frame is 2 header pulses plus 24 data pulses.
    assert (buffer[1] << 8) | buffer[2] == 26

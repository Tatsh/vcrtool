"""
Sans-I/O protocol layer for the devices this package controls.

The classes here contain pure framing logic and perform no input or output. :py:class:`SIRCSCodec`
turns a :py:class:`SIRCSCommand` into a tuple of :py:class:`Pulse` intervals (the modulated carrier
"marks" and silent "spaces" of an infrared frame) and reverses the process, while
:py:class:`JLIPCodec` builds JLIP request frames and validates response frames. The transport
classes in :py:mod:`vcrtool.sircs` and :py:mod:`vcrtool.jlip` drive the actual hardware using the
bytes and pulses produced here, which keeps the protocol logic trivially testable without devices
or real-time sleeping.

The SIRCS timing values follow the canonical Sony specification where every interval is a multiple
of a single unit ``T`` of 600 microseconds, and each frame is padded to a fixed 45 millisecond
period.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple
import enum

from .utils import pad_right

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

__all__ = (
    'CARRIER_FREQUENCY_HZ',
    'FRAME_DURATION_US',
    'ONE_MARK_US',
    'SPACE_US',
    'START_MARK_US',
    'UNIT_US',
    'ZERO_MARK_US',
    'CommandStatus',
    'JLIPCodec',
    'Pulse',
    'SIRCSCodec',
    'SIRCSCommand',
    'SIRCSVariant',
    'checksum',
)

CARRIER_FREQUENCY_HZ = 40_000
"""Nominal infrared carrier frequency in hertz.

:meta hide-value:
"""
UNIT_US = 600
"""Base SIRCS timing unit ``T`` in microseconds. Every other interval is a multiple of this value.

:meta hide-value:
"""
START_MARK_US = 4 * UNIT_US
"""Duration of the leading start (header) mark in microseconds.

:meta hide-value:
"""
ONE_MARK_US = 2 * UNIT_US
"""Duration of the mark that encodes a logical one, in microseconds.

:meta hide-value:
"""
ZERO_MARK_US = UNIT_US
"""Duration of the mark that encodes a logical zero, in microseconds.

:meta hide-value:
"""
SPACE_US = UNIT_US
"""Duration of the silent space that separates every mark, in microseconds.

:meta hide-value:
"""
FRAME_DURATION_US = 45_000
"""Total period of a single SIRCS frame in microseconds. The trailing space is stretched to it.

:meta hide-value:
"""

_TOLERANCE = 0.3
"""Fractional tolerance applied when matching a received mark against its nominal duration."""
_JLIP_FRAME_LENGTH = 10
"""Number of payload bytes a JLIP frame is checksummed over."""


class Pulse(NamedTuple):
    """A single carrier interval that makes up part of a SIRCS frame."""
    carrier_on: bool
    """Whether the carrier is modulated (a mark) or silent (a space)."""
    duration_us: int
    """Duration of the interval in microseconds."""


class SIRCSVariant(enum.Enum):
    """
    A SIRCS frame width.

    Each member's value is a ``(command_bits, address_bits, extended_bits)`` tuple describing how
    the payload is partitioned.
    """
    TWELVE_BIT = (7, 5, 0)
    """Twelve-bit frame: a 7-bit command and a 5-bit address."""
    FIFTEEN_BIT = (7, 8, 0)
    """Fifteen-bit frame: a 7-bit command and an 8-bit address."""
    TWENTY_BIT = (7, 5, 8)
    """Twenty-bit frame: a 7-bit command, a 5-bit address, and an 8-bit extended field."""
    @property
    def address_bits(self) -> int:
        """
        Number of address bits in this variant.

        Returns
        -------
        int
        """
        return self.value[1]

    @property
    def command_bits(self) -> int:
        """
        Number of command bits in this variant.

        Returns
        -------
        int
        """
        return self.value[0]

    @property
    def extended_bits(self) -> int:
        """
        Number of extended bits in this variant.

        Returns
        -------
        int
        """
        return self.value[2]

    @property
    def total_bits(self) -> int:
        """
        Total number of payload bits in this variant.

        Returns
        -------
        int
        """
        return sum(self.value)


class SIRCSCommand(NamedTuple):
    """A SIRCS payload independent of its wire representation."""
    command: int
    """The 7-bit command (button) code."""
    address: int
    """The device address."""
    extended: int = 0
    """The extended field. Only meaningful for :py:attr:`SIRCSVariant.TWENTY_BIT`."""
    variant: SIRCSVariant = SIRCSVariant.TWELVE_BIT
    """The frame width that determines how the fields are packed."""


class CommandStatus(enum.IntEnum):
    """JLIP command status codes."""
    COMMAND_ACCEPTED = 3
    """Command accepted."""
    COMMAND_ACCEPTED_NOT_COMPLETE = 4
    """Command accepted but not complete."""
    COMMAND_NOT_IMPLEMENTED = 1
    """Command not implemented."""
    COMMAND_NOT_POSSIBLE = 5
    """Command not possible."""


def checksum(vals: Sequence[int]) -> int:
    """
    Compute the checksum for a JLIP frame.

    Parameters
    ----------
    vals : Sequence[int]
        The first ten bytes of the frame to checksum.

    Returns
    -------
    int
        The computed checksum.
    """
    total = 0x80
    for i in range(_JLIP_FRAME_LENGTH):
        total -= vals[i] & 0x7F
    return total & 0x7F


class SIRCSCodec:
    """Sans-I/O encoder and decoder for SIRCS infrared frames."""
    @staticmethod
    def decode(pulses: Iterable[Pulse]) -> SIRCSCommand:
        """
        Decode the first frame of a pulse train back into a command.

        Only the marks are inspected; spaces are ignored because their durations carry no
        information beyond separating marks. The variant is inferred from the number of data bits
        found. Trailing pulses beyond the first complete frame are ignored, which lets a captured
        repeated signal be decoded directly.

        Parameters
        ----------
        pulses : Iterable[Pulse]
            The marks and spaces to decode.

        Returns
        -------
        SIRCSCommand
            The recovered payload.

        Raises
        ------
        ValueError
            If no start mark is present, a mark does not match a known duration, or the number of
            data bits does not correspond to a known variant.
        """
        marks = [pulse.duration_us for pulse in pulses if pulse.carrier_on]
        if not marks or abs(marks[0] - START_MARK_US) > START_MARK_US * _TOLERANCE:
            msg = 'Pulse train does not begin with a start mark.'
            raise ValueError(msg)
        bits: list[int] = []
        for mark in marks[1:]:
            if abs(mark - START_MARK_US) <= START_MARK_US * _TOLERANCE:
                # A second start mark begins the next repeated frame, so the first frame ends here.
                break
            if abs(mark - ONE_MARK_US) <= ONE_MARK_US * _TOLERANCE:
                bits.append(1)
            elif abs(mark - ZERO_MARK_US) <= ZERO_MARK_US * _TOLERANCE:
                bits.append(0)
            else:
                msg = f'Mark of {mark} us matches neither a zero nor a one.'
                raise ValueError(msg)
        match len(bits):
            case 12:
                variant = SIRCSVariant.TWELVE_BIT
            case 15:
                variant = SIRCSVariant.FIFTEEN_BIT
            case 20:
                variant = SIRCSVariant.TWENTY_BIT
            case count:
                msg = f'{count} data bits do not correspond to a known SIRCS variant.'
                raise ValueError(msg)
        packed = sum(bit << position for position, bit in enumerate(bits))
        return SIRCSCommand(
            command=packed & ((1 << variant.command_bits) - 1),
            address=(packed >> variant.command_bits) & ((1 << variant.address_bits) - 1),
            extended=(packed >> (variant.command_bits + variant.address_bits))
            & ((1 << variant.extended_bits) - 1),
            variant=variant)

    @staticmethod
    def encode(command: SIRCSCommand, *, repeat: int = 1) -> tuple[Pulse, ...]:
        """
        Encode a command into the pulse train of one or more frames.

        Bits are transmitted least-significant first, ordered command, then address, then extended
        field. Every frame begins with a start mark and is padded with a final space so that its
        total duration equals :py:data:`FRAME_DURATION_US`.

        Parameters
        ----------
        command : SIRCSCommand
            The payload to encode.
        repeat : int
            Number of identical frames to emit back to back. Real receivers expect at least three.

        Returns
        -------
        tuple[Pulse, ...]
            The marks and spaces for ``repeat`` consecutive frames.

        Raises
        ------
        ValueError
            If ``repeat`` is less than one or any field does not fit in its variant's bit width.
        """
        if repeat < 1:
            msg = f'repeat must be at least 1, got {repeat}.'
            raise ValueError(msg)
        variant = command.variant
        fields = ((command.command, variant.command_bits,
                   'command'), (command.address, variant.address_bits, 'address'),
                  (command.extended, variant.extended_bits, 'extended'))
        for value, width, name in fields:
            if not 0 <= value < (1 << width):
                msg = f'{name} value {value} does not fit in {width} bits.'
                raise ValueError(msg)
        packed = (command.command | (command.address << variant.command_bits)
                  | (command.extended << (variant.command_bits + variant.address_bits)))
        frame = [
            Pulse(carrier_on=True, duration_us=START_MARK_US),
            Pulse(carrier_on=False, duration_us=SPACE_US)
        ]
        for position in range(variant.total_bits):
            mark = ONE_MARK_US if (packed >> position) & 1 else ZERO_MARK_US
            frame.extend((Pulse(carrier_on=True,
                                duration_us=mark), Pulse(carrier_on=False, duration_us=SPACE_US)))
        elapsed = sum(pulse.duration_us for pulse in frame[:-1])
        frame[-1] = Pulse(carrier_on=False, duration_us=max(SPACE_US, FRAME_DURATION_US - elapsed))
        return tuple(frame) * repeat


class JLIPCodec:
    """Sans-I/O builder and validator for JLIP command frames."""
    @staticmethod
    def build_command(jlip_id: int, *args: int) -> bytes:
        """
        Build the bytes of a JLIP request frame.

        Parameters
        ----------
        jlip_id : int
            The JLIP ID of the target device.
        *args : int
            The command bytes, right-padded with zeros to fill the frame.

        Returns
        -------
        bytes
            The eleven-byte frame, including its trailing checksum.
        """
        frame = (255, 255, jlip_id, *pad_right(0, args, 7))
        return bytes([*frame, checksum(frame)])

    @staticmethod
    def validate_response(data: bytes, *, raise_on_error: bool = True) -> bytes:
        """
        Validate a JLIP response frame.

        Parameters
        ----------
        data : bytes
            The eleven-byte response frame.
        raise_on_error : bool
            If ``True``, raise when the device reports an unaccepted status.

        Returns
        -------
        bytes
            The response frame unchanged.

        Raises
        ------
        ValueError
            If the checksum does not match or, when ``raise_on_error`` is ``True``, the command
            status is not accepted.
        """
        if data[10] != (actual := checksum(list(data)[:_JLIP_FRAME_LENGTH])):
            msg = f'Checksum did not match. Expected {actual} but received {data[10]}.'
            raise ValueError(msg)
        status = data[3] & 0b111
        if raise_on_error and status not in {
                CommandStatus.COMMAND_ACCEPTED, CommandStatus.COMMAND_ACCEPTED_NOT_COMPLETE
        }:
            msg = f'Command status: {CommandStatus(status)!s}'
            raise ValueError(msg)
        return data

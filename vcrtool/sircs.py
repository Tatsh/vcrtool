"""SIRCS (Sony Infrared Remote Control System) transport over a Raspberry Pi Pico."""
from __future__ import annotations

from typing import TYPE_CHECKING

import serial

from .sansio import SIRCSCodec

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .sansio import Pulse, SIRCSCommand

__all__ = ('PicoSIRCSTransport',)

_PICO_SYNC = 0xA5
"""Synchronisation byte that begins every message sent to the Pico."""
_UINT16_MAX = 0xFFFF
"""Largest value a 16-bit field can carry."""


class PicoSIRCSTransport:
    """
    Transport that delegates SIRCS timing to a Raspberry Pi Pico over USB serial.

    The protocol framing lives in :py:class:`~vcrtool.sansio.SIRCSCodec`. This class serialises the
    pulse train it produces into a compact message and writes it to the Pico, whose firmware clocks
    the pin edges out with a PIO state machine for jitter-free timing. The PC therefore keeps all
    protocol knowledge and the Pico stays a dumb, precisely-timed output peripheral.

    The message is a sync byte, a 16-bit big-endian pulse count, and then one three-byte record per
    pulse: a level byte followed by a 16-bit big-endian duration in microseconds. The level is the
    final pin state, so ``invert`` (used for an active-low ``CONTROL S`` jack) is resolved here and
    the firmware simply holds the pin at the given level.
    """
    def __init__(self, serial_path: str, *, baud_rate: int = 115_200, invert: bool = False) -> None:
        """
        Open the serial connection to the Pico.

        Parameters
        ----------
        serial_path : str
            Path to the Pico's USB serial device.
        baud_rate : int
            Baud rate of the serial connection.
        invert : bool
            If ``True``, a mark is sent as a low level and a space as a high level.
        """
        self.codec = SIRCSCodec()
        """The sans-I/O codec used to build pulse trains."""
        self.comm = serial.Serial(serial_path, baudrate=baud_rate, timeout=2)
        """Serial connection to the Pico."""
        self._invert = invert

    @staticmethod
    def serialize(pulses: Iterable[Pulse], *, invert: bool = False) -> bytes:
        """
        Serialise a pulse train into the Pico wire message.

        Parameters
        ----------
        pulses : Iterable[Pulse]
            The marks and spaces to serialise.
        invert : bool
            If ``True``, mark and space levels are swapped.

        Returns
        -------
        bytes
            The complete message, ready to write to the Pico.

        Raises
        ------
        ValueError
            If any pulse duration or the pulse count does not fit in 16 bits.
        """
        records = bytearray()
        count = 0
        for pulse in pulses:
            if not 0 <= pulse.duration_us <= _UINT16_MAX:
                msg = f'Pulse duration {pulse.duration_us} us does not fit in 16 bits.'
                raise ValueError(msg)
            records += bytes((int(pulse.carrier_on != invert), (pulse.duration_us >> 8) & 0xFF,
                              pulse.duration_us & 0xFF))
            count += 1
        if count > _UINT16_MAX:
            msg = f'Too many pulses to serialise: {count}.'
            raise ValueError(msg)
        return bytes((_PICO_SYNC, (count >> 8) & 0xFF, count & 0xFF)) + bytes(records)

    def send_command(self, command: SIRCSCommand, *, repeat: int = 3) -> None:
        """
        Encode a command and send it to the Pico.

        Parameters
        ----------
        command : SIRCSCommand
            The payload to send.
        repeat : int
            Number of identical frames to play. Sony receivers expect at least three.
        """
        self.transmit(self.codec.encode(command, repeat=repeat))

    def transmit(self, pulses: Iterable[Pulse]) -> None:
        """
        Serialise a pulse train and write it to the Pico.

        Parameters
        ----------
        pulses : Iterable[Pulse]
            The marks and spaces to transmit.
        """
        self.comm.write(self.serialize(pulses, invert=self._invert))

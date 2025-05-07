"""SIRCS (Sony Infrared Remote Control System) functionality."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pyftdi.gpio import GpioAsyncController  # type: ignore[import-untyped]

from .utils import debug_sleep

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = ('SIRCS',)


class SIRCS:
    """SIRCS (Sony Infrared Remote Control System) handling class."""
    def __init__(self, ftdi_url: str = 'ftdi://0x403:0x6001/1') -> None:
        self.gpio = GpioAsyncController()
        self.gpio.open_from_url(ftdi_url, 0b11111111)

    def logic1(self) -> None:
        """Set the GPIO to logic 1."""
        self.gpio.write(255)

    def logic0(self) -> None:
        """Set the GPIO to logic 0."""
        self.gpio.write(0)

    def send_command(self, bits: Iterable[int]) -> None:
        """Send a command to the SIRCS device."""
        total_time = 0.0
        for bit in bits:
            self.logic1()
            if bit:
                debug_sleep(0.0012)
                total_time += 0.0012
            else:
                debug_sleep(0.0006)
                total_time += 0.0006
            self.logic0()
            debug_sleep(0.0006)
            total_time += 0.0006
        debug_sleep(max(0, 0.045 - total_time))

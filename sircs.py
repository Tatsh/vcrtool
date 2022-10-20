from time import sleep
from typing import Sequence

from pyftdi.gpio import GpioAsyncController
import click


class SIRCS:
    def __init__(self, ftdi_url: str = 'ftdi://0x403:0x6001/1'):
        self._gpio = GpioAsyncController()
        self._gpio.open_from_url(ftdi_url, 0b11111111)

    def logic1(self) -> None:
        self._gpio.write(255)

    def logic0(self) -> None:
        self._gpio.write(0)

    def send_command(self, bits: Sequence[int]):
        total_time = 0.0
        for bit in bits:
            self.logic1()
            if bit:
                sleep(0.0012)
                total_time += 0.0012
            else:
                sleep(0.0006)
                total_time += 0.0006
            self.logic0()
            sleep(0.0006)
            total_time += 0.0006
        sleep(max(0, 0.045 - total_time))


@click.command()
def main() -> None:
    SIRCS().send_command(b'\x00')

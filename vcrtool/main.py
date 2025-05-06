"""Main script."""
from __future__ import annotations

from pathlib import Path

import click

from .utils import SIRCS, CommandStatus, JLIPHRSeriesVCR, setup_logging

__all__ = ('jlip_commands', 'jlip_presence_check', 'sircs')


@click.command()
@click.argument('devpath')
def jlip_presence_check(devpath: str) -> None:
    setup_logging()
    for i in range(1, 100):
        try:
            if ((JLIPHRSeriesVCR(devpath,
                                 jlip_id=i, raise_on_error_response=False).send_command_fast(
                                     0x7c, 0x4e, 0x20)[3]
                 & 0b111) == CommandStatus.COMMAND_ACCEPTED) and not Path(f'/dev/jlip{i}').exists():
                click.echo(i)
                break
        except IndexError:
            continue


@click.command()
def sircs() -> None:
    setup_logging()
    SIRCS().send_command(b'\x00')


@click.command()
@click.argument('serial_device')
@click.argument('commands', nargs=-1)
def jlip_commands(serial_device: str, commands: list[str]) -> None:
    setup_logging()
    vcr = JLIPHRSeriesVCR(serial_device, raise_on_error_response=False)
    disallowed = ('send_command', 'send_command_fast')
    for _command in (x for x in commands
                     if x not in disallowed and getattr(vcr, x, None) is not None):
        pass

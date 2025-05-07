"""Main script."""
# ruff: noqa: DOC501
from __future__ import annotations

import dataclasses
import inspect
import json

import click

from .jlip import JLIP
from .utils import setup_logging

__all__ = ('jlip',)

DISALLOWED_COMMANDS = {'send_command_base', 'send_command_fast'}
VALID_COMMANDS = [
    name.replace('_', '-') for name, x in inspect.getmembers(JLIP)
    if callable(x) and not name.startswith('_') and name not in DISALLOWED_COMMANDS
]


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument('serial_device')
@click.argument('args', nargs=-1)
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
def jlip(serial_device: str, args: tuple[str, ...], *, debug: bool = False) -> None:
    """Run JLIP commands."""
    setup_logging(debug=debug)
    try:
        command = args[0]
    except IndexError as e:
        msg = 'No command provided.'
        raise click.BadArgumentUsage(msg) from e
    if not command or command not in VALID_COMMANDS:
        msg = f'Invalid command `{command}`. Valid commands: {", ".join(VALID_COMMANDS)}.'
        raise click.BadArgumentUsage(msg)
    vcr = JLIP(serial_device, raise_on_error_response=False)
    click.echo(
        json.dumps(
            dataclasses.asdict(
                getattr(vcr, command.replace('-', '_'))(*(int(x) for x in args[1:])))))

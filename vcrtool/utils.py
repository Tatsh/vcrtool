"""Utilities."""
from __future__ import annotations

from shlex import quote
from time import sleep
from typing import TYPE_CHECKING, Any, TypeVar
import asyncio
import asyncio.subprocess as asp
import logging
import logging.config
import re
import subprocess as sp

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ('adebug_create_subprocess_exec', 'adebug_sleep', 'audio_device_is_available',
           'debug_sleep', 'debug_sp_run', 'get_pipewire_audio_device_node_id', 'pad_right',
           'setup_logging')

log = logging.getLogger(__name__)

T = TypeVar('T')


def pad_right(value: T, list_: Sequence[T], max_length: int) -> list[T]:
    """
    Pad a sequence to the right with a value.

    Returns
    -------
    list[T]

    Raises
    ------
    ValueError
    """
    if (diff := max_length - len(list_)) < 0:
        raise ValueError(diff)
    return list(list_) + (diff * [value])


def setup_logging(*,
                  debug: bool = False,
                  force_color: bool = False,
                  no_color: bool = False) -> None:  # pragma: no cover
    """Set up logging configuration."""
    logging.config.dictConfig({
        'disable_existing_loggers': True,
        'root': {
            'level': 'DEBUG' if debug else 'INFO',
            'handlers': ['console'],
        },
        'formatters': {
            'default': {
                '()': 'colorlog.ColoredFormatter',
                'force_color': force_color,
                'format': (
                    '%(light_cyan)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s | '
                    '%(light_green)s%(name)s%(reset)s:%(light_red)s%(funcName)s%(reset)s:'
                    '%(blue)s%(lineno)d%(reset)s - %(message)s'),
                'no_color': no_color,
            }
        },
        'handlers': {
            'console': {
                'class': 'colorlog.StreamHandler',
                'formatter': 'default',
            }
        },
        'version': 1
    })


def debug_sp_run(*args: Any, **kwargs: Any) -> sp.CompletedProcess[Any]:
    """
    Run a subprocess and log the command at the :py:obj:`logging.DEBUG` level.

    Returns
    -------
    sp.CompletedProcess[Any]
    """
    log.debug('Executing: %s', ' '.join(quote(x) for x in list(args[0])))
    return sp.run(*args, **kwargs, check=False)


def audio_device_is_available(audio_device: str) -> bool:
    """
    Check if an ALSA device can be used by attempting to open it with ffmpeg.

    Returns
    -------
    bool
    """
    log.debug('Checking if %s can be used.', audio_device)
    return 'Device or resource busy' not in debug_sp_run(
        ('ffmpeg', '-hide_banner', '-f', 'alsa', '-i', audio_device),
        capture_output=True,
        text=True).stderr


def get_pipewire_audio_device_node_id(name: str) -> tuple[str, str] | tuple[None, None]:
    """
    Get the Pipewire node ID of an ALSA device.

    Parameters
    ----------
    name : str
        The name of the audio device.

    Returns
    -------
    tuple[str, str] | tuple[None, None]
        The name and node ID of the audio device, or (None, None) if not found.

    Raises
    ------
    ValueError
        If the ALSA device string is invalid.
    """
    log.debug('Getting node ID for "%s".', name)
    if (m := re.match(r'^hw:(\d+),(\d+)$', name)):
        card, device = m.groups()
        log.debug('card = %s, device = %s', card, device)
        name = next(item for item in debug_sp_run(('udevadm', 'info', '--attribute-walk',
                                                   f'/dev/snd/pcmC{card}D{device}c'),
                                                  text=True,
                                                  capture_output=True,
                                                  check=True).stdout.splitlines()
                    if 'ATTRS{product}==' in item).split('"')[1]
    else:
        msg = f'Invalid ALSA device string: {name}'
        raise ValueError(msg)
    lines = debug_sp_run(('wpctl', 'status'), text=True, capture_output=True,
                         check=True).stdout.splitlines()
    try:
        res = next(item for item in lines if name in item).split('.')[0]
        if m := re.search(r'(\d+)$', res):
            log.debug('Found node ID %s', m[0])
            return name, m[0]
    except (IndexError, StopIteration):
        pass
    log.debug('Failed to get node ID')
    return None, None


async def adebug_sleep(interval: float) -> None:
    """Sleep for a given interval and log the sleep time at the :py:obj:`logging.DEBUG` level."""
    log.debug('Sleeping for %s %s.', interval,
              'seconds' if interval == 0 or interval > 1 else 'second')
    await asyncio.sleep(interval)


def debug_sleep(interval: float) -> None:
    """Sleep for a given interval and log the sleep time at the :py:obj:`logging.DEBUG` level."""
    log.debug('Sleeping for %s %s.', interval,
              'seconds' if interval == 0 or interval > 1 else 'second')
    sleep(interval)


async def adebug_create_subprocess_exec(*args: Any, **kwargs: Any) -> asp.Process:
    """
    Run a subprocess and log the command at the :py:obj:`logging.DEBUG` level.

    Returns
    -------
    asp.CompletedProcess[Any]
    """
    log.debug('Executing: %s', ' '.join(quote(x) for x in list(args)))
    return await asp.create_subprocess_exec(*args, **kwargs)

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn, ParamSpec, TypeVar, cast
import asyncio
import asyncio.subprocess as asp
import logging
import subprocess as sp
import sys

from pytimeparse2 import parse as timeparse  # type: ignore[import-untyped]
import click
import psutil

from .utils import (
    JLIPHRSeriesVCR,
    VTRMode,
    adebug_create_subprocess_exec,
    adebug_sleep,
    audio_device_is_available,
    debug_sleep,
    get_pipewire_audio_device_node_id,
)

DEFAULT_TIMESPAN = '372m'
THREAD_QUEUE_SIZE = 2048

P = ParamSpec('P')
T = TypeVar('T')
C = TypeVar('C', bound=Callable[..., Any])

log = logging.getLogger(__name__)


async def _a_main(video_device: str, audio_device: str, length: int, output: str, input_index: int,
                  vbi_device: str | None, vcr: JLIPHRSeriesVCR) -> int:
    log.debug('Starting ffmpeg')
    length = int(length) + 15
    log.debug('Will record for %s seconds', length)
    output_base = Path(output).stem
    ffmpeg_proc = await adebug_create_subprocess_exec(
        'ffmpeg',
        '-hide_banner',
        '-loglevel',
        'warning',
        '-y',
        '-thread_queue_size',
        str(THREAD_QUEUE_SIZE),
        '-f',
        'v4l2',
        '-i',
        video_device,
        '-thread_queue_size',
        str(THREAD_QUEUE_SIZE),
        '-f',
        'alsa',
        '-i',
        audio_device,
        '-c:a',
        'flac',
        '-ac',
        '2',
        '-c:v',
        'libx265',
        '-x265-params',
        'lossless=1',
        '-preset',
        'superfast',
        '-flags',
        '+ilme+ildct',
        '-top',
        '1',
        '-aspect',
        '4/3',
        '-t',
        str(length),
        output,
        env={'FFREPORT': f'file={output_base}.log:level=40'},
        stdin=asp.PIPE)
    log.debug('ffmpeg PID: %s', ffmpeg_proc.pid)
    vbi_proc = None
    if vbi_device:
        output_vbi = f'{output_base}.vbi'
        Path(output_vbi).unlink(missing_ok=True)
        log.debug('Starting zvbi2raw with device %s and outputting to %s', vbi_device, output_vbi)
        vbi_proc = await adebug_create_subprocess_exec('zvbi2raw',
                                                       '-d',
                                                       vbi_device,
                                                       '-o',
                                                       f'{output_base}.vbi',
                                                       stdout=asp.PIPE,
                                                       stderr=asp.PIPE,
                                                       stdin=asp.PIPE)
        log.debug('zvbi2raw PID: %d', vbi_proc.pid)
    else:
        log.debug('VBI device not specified')
    await adebug_sleep(2)
    log.debug('Setting device %s input to %s', video_device, input_index)
    change_input_proc = await adebug_create_subprocess_exec('v4l2-ctl',
                                                            '-d',
                                                            video_device,
                                                            '-i',
                                                            str(input_index),
                                                            stdout=asp.PIPE,
                                                            stderr=asp.PIPE,
                                                            stdin=asp.PIPE)
    log.debug('v4l2-ctl PID: %d', change_input_proc.pid)
    await change_input_proc.wait()
    log.debug('v4l2-ctl exited with code %d', change_input_proc.returncode)
    if change_input_proc.returncode != 0:
        log.error('Failed to set input.')
        raise click.Abort
    await adebug_sleep(0.25)
    log.debug('Resetting VCR counter')
    vcr.reset_counter()
    await adebug_sleep(1)
    log.debug('Starting VCR playback')
    vcr.play()
    ffmpeg_pid = ffmpeg_proc.pid
    try:
        while psutil.pid_exists(ffmpeg_pid):
            data = vcr.get_vtr_mode(fast=True)
            if data.vtr_mode != VTRMode.PLAY_FWD:
                log.debug('Detected VCR is no longer playing (mode = %s). Terminating ffmpeg.',
                          data.vtr_mode)
                ffmpeg_proc.terminate()
                break
    except KeyboardInterrupt:
        log.info('Received keyboard interrupt. Terminating ffmpeg.')
        ffmpeg_proc.terminate()
    # Waiting is required to avoid 'Loop that handles pid ... is closed'
    ffmpeg_proc_return = await ffmpeg_proc.wait()
    log.debug('ffmpeg exited with code %d', ffmpeg_proc_return)
    # ffmpeg always sets 255 if interrupted, but generally makes the file ready for use
    if ffmpeg_proc_return not in {0, 255}:
        log.warning('ffmpeg did not exit cleanly')
        return 1
    vbi_proc_return = None
    if vbi_proc:
        try:
            log.debug('Terminating zvbi2raw')
            vbi_proc.terminate()
            vbi_proc_return = await vbi_proc.wait()
        except ProcessLookupError:
            pass
        log.debug('zvbi2raw exited with code %d. Ignoring.', vbi_proc_return or vbi_proc.returncode)
    return 0


@click.command()
@click.option('-a', '--audio-device', required=True)
@click.option('-b', '--vbi-device')
@click.option('-i', '--input-index', default=2, type=int)
@click.option('-s', '--serial', required=True)
@click.option('-t', '--timespan', default=DEFAULT_TIMESPAN)
@click.option('-v', '--video-device', required=True)
@click.argument('output')
def main(serial: str, audio_device: str, video_device: str, vbi_device: str | None,
         timespan: str | None, output: str, input_index: int) -> NoReturn:
    timespan_seconds = timeparse(timespan or DEFAULT_TIMESPAN)
    if not timespan_seconds:
        click.secho('Timespan is invalid.', file=sys.stderr)
        raise click.Abort
    audio_device_name, audio_node_id = get_pipewire_audio_device_node_id(audio_device)
    if not audio_node_id:
        click.secho('Unable to find audio node ID.', file=sys.stderr)
        raise click.Abort
    log.debug('Setting Pipewire device "%s" to Off', audio_device_name)
    sp.run(('wpctl', 'set-profile', audio_node_id, '0'), check=True)
    debug_sleep(0.1)
    if not audio_device_is_available(audio_device):
        click.secho('Cannot use audio device.', file=sys.stderr)
        raise click.Abort
    vcr = JLIPHRSeriesVCR(serial)
    log.debug('Turning VCR on')
    vcr.turn_on()
    if not vcr.get_vtr_mode().tape_inserted:
        log.error('No tape inserted')
        raise click.Abort
    log.debug('Rewinding tape')
    vcr.rewind_wait()
    log.debug('Entering async')
    ret = asyncio.run(
        _a_main(video_device, audio_device, cast('int', timespan_seconds), output, input_index,
                vbi_device, vcr))
    log.debug('Exiting async')
    log.debug('Setting Pipewire device "%s" to On', audio_device_name)
    sp.run(('wpctl', 'set-profile', audio_node_id, '1'), check=True)
    log.debug('Rewinding tape')
    vcr.rewind_wait()
    sys.exit(ret)

"""Utilities."""
from __future__ import annotations

from shlex import quote
from time import sleep
from typing import TYPE_CHECKING, Any, NamedTuple, TypeVar, cast
import asyncio
import asyncio.subprocess as asp
import enum
import logging
import logging.config
import re
import subprocess as sp

from pyftdi.gpio import GpioAsyncController  # type: ignore[import-untyped]
from pyrate_limiter import Duration, Limiter, RequestRate  # type: ignore[attr-defined]
from typing_extensions import override
import serial

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ('SIRCS', 'BandInfo', 'CommandResponse', 'CommandStatus', 'JLIPHRSeriesVCR',
           'PowerStateResponse', 'ResponseTuple', 'VTRMode', 'VTRModeResponse', 'VTUModeResponse',
           'setup_logging')

log = logging.getLogger(__name__)
limiter = Limiter(RequestRate(2, Duration.SECOND))
fast_limiter = Limiter(RequestRate(10, Duration.SECOND))
T = TypeVar('T')


class SIRCS:
    def __init__(self, ftdi_url: str = 'ftdi://0x403:0x6001/1') -> None:
        self._gpio = GpioAsyncController()
        self._gpio.open_from_url(ftdi_url, 0b11111111)

    def logic1(self) -> None:
        self._gpio.write(255)

    def logic0(self) -> None:
        self._gpio.write(0)

    def send_command(self, bits: Sequence[int]) -> None:
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


def checksum(vals: list[int]) -> int:
    sum_ = 0x80
    for i in range(10):
        sum_ -= (vals[i] & 0x7F)
    return sum_ & 0x7F


def pad_right(value: Any, list_: Sequence[T], max_length: int) -> list[T]:
    if (diff := max_length - len(list_)) < 0:
        raise ValueError(diff)
    return list(list_) + (diff * [value])


class CommandStatus(enum.IntEnum):
    COMMAND_ACCEPTED = 3
    COMMAND_ACCEPTED_NOT_COMPLETE = 4
    COMMAND_NOT_IMPLEMENTED = 1
    COMMAND_NOT_POSSIBLE = 5


class ResponseTuple(NamedTuple):
    jlip_id: int
    command_status: CommandStatus
    return_data: bytes

    def __repr__(self) -> str:
        return (f'ResponseTuple(jlip_id={self.jlip_id}, '
                f'command_status={self.command_status!s}, '
                f'return_data=[{", ".join(hex(n) for n in self.return_data[1:])}])')


class CommandResponse:
    def __init__(self, resp: bytes) -> None:
        self.checksum = resp[10]
        self.raw = resp
        self.return_data = resp[3:10]
        self.status = CommandStatus(resp[3] & 0b111)
        self.tuple = ResponseTuple(resp[2], CommandStatus(resp[3] & 0b111), resp[4:10])

    def __repr__(self) -> str:
        return ('<CommandResponse '
                f'checksum={hex(self.checksum)} '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s}'
                '>')


class VTRMode(enum.IntEnum):
    EJECT = 0
    FF = 0b10
    NO_MODE = 0b1111
    PAUSE = 0b111
    PLAY_BWD = 0b101
    PLAY_FWD = 0b110
    REC = 0b1110
    REC_PAUSE = 0b1101
    REW = 0b11
    STOP = 1


NTSC_FRAMERATE = 30
PAL_FRAMERATE = 25


class VTRModeResponse(CommandResponse):
    def __init__(self, resp: bytes) -> None:
        super().__init__(resp)
        self.drop_frame_mode_enabled = bool(resp[5] & 1)
        self.framerate = 25 if ((resp[5] >> 2) & 1) == 1 else 30
        self.hour, self.minute, self.second, self.frame = resp[6:10]
        self.is_ntsc = self.framerate == NTSC_FRAMERATE
        self.is_pal = self.framerate == PAL_FRAMERATE
        self.recordable = not bool(resp[4] >> 5 & 1)
        self.tape_inserted = ((resp[4] >> 4) & 1) == 0
        self.vtr_mode = VTRMode((resp[4]) & 0b1111)

    def __repr__(self) -> str:
        return ('<VTRModeResponse '
                f'checksum={hex(self.checksum)} '
                f'counter="{self.hour:02}:{self.minute:02}:{self.second:02}:{self.frame:06}" '
                f'drop_framerate_mode_enabled={self.drop_frame_mode_enabled} '
                f'framerate={self.framerate} '
                f'is_ntsc={self.is_ntsc} '
                f'is_pal={self.is_pal} '
                f'recordable={self.recordable} '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s} '
                f'tape_inserted={self.tape_inserted} '
                f'vtr_mode={self.vtr_mode!s}'
                '>')


class BandInfo(enum.IntEnum):
    BROADCAST_SATELLITE = 0x40
    TERRESTRIAL_BROADCAST = 0x30


BANK_NUMBER_NONE = 0x51


class VTUModeResponse(CommandResponse):
    def __init__(self, resp: bytes) -> None:
        super().__init__(resp)
        self.band_info = BandInfo(resp[4])
        self.bank_number = None if resp[5] == BANK_NUMBER_NONE else resp[6] - 100
        self.channel_number_by_bank = None if resp[5] == BANK_NUMBER_NONE else resp[7]
        self.channel_number_non_bank = (resp[6] * 100) + resp[7]
        self.real_channel = resp[5]

    @override
    def __repr__(self) -> str:
        return ('<VTUModeResponse '
                f'band_info={self.band_info!s} '
                f'bank_number={self.bank_number!s} '
                f'channel_number_by_bank={self.channel_number_by_bank} '
                f'channel_number_non_bank={self.channel_number_non_bank} '
                f'checksum={hex(self.checksum)} '
                f'real_channel={self.real_channel} '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s}'
                '>')


class PowerStateResponse(CommandResponse):
    def __init__(self, resp: bytes) -> None:
        super().__init__(resp)
        self.is_on = bool(resp[4])

    @override
    def __repr__(self) -> str:
        return ('<PowerStateResponse '
                f'checksum={hex(self.checksum)} '
                f'is_on={self.is_on} '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s}'
                '>')


class DeviceNameResponse(CommandResponse):
    def __init__(self, resp: bytes) -> None:
        super().__init__(resp)
        self.name = ''.join(chr(x) for x in self.return_data)

    @override
    def __repr__(self) -> str:
        return ('<DeviceNameResponse '
                f'checksum={hex(self.checksum)} '
                f'name="{self.name}" '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s}'
                '>')


class JLIPHRSeriesVCR:  # noqa: PLR0904
    """Class to run commands against HR-S9600U and similar VCRs over JLIP.

    References
    ----------
        - http://www.johnwillis.com/2018/09/jvc-jlip-joint-level-interface-protocol.html
        - https://dragonminded.com/bemani/dvdemu/JLIPProtocolDocumentation.pdf
        - https://github.com/yasdfgr/jlip
        - https://jvc-america.com/english/download/mpverup114-e.html
        - https://www.remotecentral.com/cgi-bin/forums/viewpost.cgi?1040370
    """
    def __init__(self,
                 serial_path: str,
                 *,
                 jlip_id: int = 1,
                 raise_on_error_response: bool = True) -> None:
        self._ser = serial.Serial(serial_path, parity=serial.PARITY_ODD, rtscts=True, timeout=2)
        self.jlip_id = jlip_id
        self._raise = raise_on_error_response

    def send_command_base(self, *args: Any) -> bytes:
        arr = cast('list[int]', [255, 255, self.jlip_id, *pad_right(0, list(args), 7)])
        self._ser.write(bytearray([*arr, checksum(arr)]))
        sleep(0.1)
        ret = self._ser.read(11)
        actual_checksum = checksum(list(ret)[:10])
        if ret[10] != actual_checksum:
            msg = (f'Checksum did not match. Expected {actual_checksum} but '
                   f'received {ret[10]}')
            raise ValueError(msg)
        status = ret[3] & 0b111
        if (self._raise and status not in {
                CommandStatus.COMMAND_ACCEPTED, CommandStatus.COMMAND_ACCEPTED_NOT_COMPLETE
        }):
            msg = f'Command status: {CommandStatus(status)!s}'
            raise ValueError(msg)
        return ret

    @limiter.ratelimit('serial', delay=True)  # type: ignore[attr-defined,misc]
    def send_command(self, *args: Any) -> bytes:
        return self.send_command_base(*args)

    @fast_limiter.ratelimit('serial_fast', delay=True)  # type: ignore[attr-defined,misc]
    def send_command_fast(self, *args: Any) -> bytes:
        return self.send_command_base(*args)

    def eject(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x41, 0x60))

    def eject_wait(self) -> CommandResponse:
        resp = self.stop()
        sleep(0.5)
        resp = self.eject()
        while (resp := self.get_vtr_mode()).vtr_mode != VTRMode.EJECT:
            sleep(0.25)
        return resp

    def fast_forward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x44, 0x75))

    def fast_play_forward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x21))

    def fast_play_backward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x25))

    def frame_step(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x48, 0x46, 0x75, 0x01))

    def frame_step_back(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x48, 0x46, 0x65, 0x01))

    def get_baud_rate_supported(self) -> CommandResponse:
        """0x21 is returned, meaning 19200 baud, but it is a lie."""
        return CommandResponse(self.send_command(0x7C, 0x48, 0x20))

    def get_device_code(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x7C, 0x49))

    def get_device_name(self) -> CommandResponse:
        return DeviceNameResponse(self.send_command(0x7C, 0x4C))

    def get_input(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x58, 0x20))

    def get_machine_code(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x7C, 0x45))

    def get_play_speed(self) -> CommandResponse:
        """
        Get playback speed.

        Known responses in the first data field:

        - `0x7F` is returned when inapplicable.
        - `0x75` means normal.
        - `0x77` means playing forward quickly.
        - `0x67` means playing backward quickly.
        - `0x6D` means paused or frame advancing.
        """
        return CommandResponse(self.send_command(0x48, 0x4E, 0x20))

    def get_power_state(self) -> PowerStateResponse:
        return PowerStateResponse(self.send_command(0x3E, 0x4E, 0x20))

    def get_tuner_mode(self) -> VTUModeResponse:
        return VTUModeResponse(self.send_command(0xA, 0x4E, 0x20))

    def get_vtr_mode(self, *, fast: bool = False) -> VTRModeResponse:
        return VTRModeResponse((self.send_command_fast if fast else self.send_command)(0x08, 0x4E,
                                                                                       0x20))

    def nop(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x7c, 0x4e, 0x20))

    def pause(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x6d))

    def pause_recording(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x42, 0x6d))

    def play(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x75))

    def preset_channel_up(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x0A, 0x44, 0x73, 0, 0, 0x7E))

    def preset_channel_down(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x0A, 0x44, 0x63, 0, 0, 0x7E))

    def real_channel_down(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x0A, 0x42, 0x63, 0, 0, 0x44))

    def real_channel_up(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x0A, 0x42, 0x73, 0, 0, 0x44))

    def record(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x42, 0x70))

    def reset_counter(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x48, 0x4D, 0x20))

    def rewind(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x44, 0x65))

    def rewind_wait(self) -> CommandResponse:
        resp = self.stop()
        sleep(1)
        resp = self.rewind()
        while (resp := self.get_vtr_mode()).vtr_mode == VTRMode.REW:
            sleep(1)
        return resp

    def set_channel(self, channel: int) -> CommandResponse:
        return CommandResponse(self.send_command(0x0a, 0x44, 0x71, 0, channel, 0x7E))

    def set_jlip_id(self, n: int) -> CommandResponse:
        if n <= 0 or n > 99:  # noqa: PLR2004
            raise ValueError(n)
        return CommandResponse(self.send_command(0x7C, 0x41, n))

    def set_input(self, n: int, nn: int) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x59, n, nn, 0x7F))

    def set_record_mode(self, n: int) -> CommandResponse:
        return CommandResponse(self.send_command(0x48, 0x43, n))

    def set_record_speed(self, n: int) -> CommandResponse:
        return CommandResponse(self.send_command(0x48, 0x42, n))

    def select_band(self, n: int) -> CommandResponse:
        return CommandResponse(self.send_command(0x0A, 0x40, 0x71, n))

    def select_preset_channel(self, n: int, nn: int, nnn: int) -> CommandResponse:
        return CommandResponse(self.send_command(0x0A, 0x44, n, nn, nnn, 0x7E))

    def select_real_channel(self, n: int, nn: int, nnn: int) -> CommandResponse:
        return CommandResponse(self.send_command(0x0A, 0x42, n, nn, nnn, 0x44))

    def slow_play_backward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x24))

    def slow_play_forward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x20))

    def stop(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x44, 0x60))

    def turn_off(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x3E, 0x40, 0x60))

    def turn_on(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x3E, 0x40, 0x70))

    @override
    def __repr__(self) -> str:
        return ('<JLIPHRSeriesVCR '
                f'jlip_id={self.jlip_id} '
                f'raise_on_error={self._raise}'
                '>')


def setup_logging(*,
                  debug: bool = False,
                  force_color: bool = False,
                  no_color: bool = False) -> None:
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
    log.debug('Executing: %s', ' '.join(quote(x) for x in list(args[0])))
    return sp.run(*args, **kwargs, check=False)


def audio_device_is_available(audio_device: str) -> bool:
    log.debug('Checking if %s can be used', audio_device)
    return 'Device or resource busy' not in debug_sp_run(
        ('ffmpeg', '-hide_banner', '-f', 'alsa', '-i', audio_device),
        capture_output=True,
        text=True).stderr


def get_pipewire_audio_device_node_id(name: str) -> tuple[str, str] | tuple[None, None]:
    log.debug('Getting node ID for "%s"', name)
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
    try:
        if (m := re.search(
                r'(\d+)$',
                next(item for item in debug_sp_run(
                    ('wpctl',
                     'status'), text=True, capture_output=True, check=True).stdout.splitlines()
                     if name in item).split('.')[0])):
            log.debug('Found node ID %s', m[0])
            return name, m[0]
    except IndexError:
        pass
    log.debug('Failed to get node ID')
    return None, None


async def adebug_sleep(interval: float) -> None:
    log.debug('Sleeping for %s %s', interval,
              'seconds' if interval == 0 or interval > 1 else 'second')
    await asyncio.sleep(interval)


def debug_sleep(interval: float) -> None:
    log.debug('Sleeping for %s %s', interval,
              'seconds' if interval == 0 or interval > 1 else 'second')
    sleep(interval)


async def adebug_create_subprocess_exec(*args: Any, **kwargs: Any) -> asp.Process:
    log.debug('Executing: %s', ' '.join(quote(x) for x in list(args)))
    return await asp.create_subprocess_exec(*args, **kwargs)

"""JLIP-specific functionality."""
from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import TYPE_CHECKING
import enum

from pyrate_limiter import Duration, Limiter, Rate
from typing_extensions import override
import serial

from .utils import pad_right

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ('JLIP', 'BandInfo', 'CommandResponse', 'CommandResponseTuple', 'CommandStatus',
           'DeviceNameResponse', 'PowerStateResponse', 'VTRMode', 'VTRModeResponse')


class CommandStatus(enum.IntEnum):
    """Command status codes."""
    COMMAND_ACCEPTED = 3
    """Command accepted."""
    COMMAND_ACCEPTED_NOT_COMPLETE = 4
    """Command accepted but not complete."""
    COMMAND_NOT_IMPLEMENTED = 1
    """Command not implemented."""
    COMMAND_NOT_POSSIBLE = 5
    """Command not possible."""


@dataclass
class CommandResponseTuple:
    """Lower-level command response information."""
    jlip_id: int
    """JLIP ID."""
    command_status: CommandStatus
    """Command status."""
    return_data: bytes
    """Return data."""
    @override
    def __repr__(self) -> str:
        return (f'<CommandResponseTuple jlip_id={self.jlip_id}, '
                f'command_status={self.command_status!s}, '
                f'return_data=[{", ".join(hex(n) for n in self.return_data[1:])}]>')


@dataclass
class CommandResponse:
    """Command response information."""
    checksum: int
    """Checksum."""
    raw: bytes
    """Raw response."""
    return_data: bytes
    """Return data."""
    status: CommandStatus
    """Command status."""
    tuple: CommandResponseTuple
    """Lower-level command response information."""
    @staticmethod
    def from_bytes(resp: bytes) -> CommandResponse:
        """Initialise from bytes."""
        return CommandResponse(
            resp[10], resp, resp[3:10], CommandStatus(resp[3] & 0b111),
            CommandResponseTuple(resp[2], CommandStatus(resp[3] & 0b111), resp[4:10]))

    @override
    def __repr__(self) -> str:
        return ('<CommandResponse '
                f'checksum={hex(self.checksum)} '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s}'
                '>')


class VTRMode(enum.IntEnum):
    """VTR mode codes."""
    EJECT = 0
    """Eject."""
    FF = 0b10
    """Fast forward."""
    NO_MODE = 0b1111
    """No mode."""
    PAUSE = 0b111
    """Pause."""
    PLAY_BWD = 0b101
    """Play backward."""
    PLAY_FWD = 0b110
    """Play forward."""
    REC = 0b1110
    """Record."""
    REC_PAUSE = 0b1101
    """Record pause."""
    REW = 0b11
    """Rewind."""
    STOP = 1
    """Stop."""


NTSC_FRAMERATE = 30
"""NTSC framerate (rounded)."""
PAL_FRAMERATE = 25
"""PAL framerate."""


@dataclass
class VTRModeResponse(CommandResponse):
    """VTR mode response information."""
    drop_frame_mode_enabled: bool
    """Drop frame mode enabled."""
    framerate: int
    """Framerate."""
    hour: int
    """Hour."""
    minute: int
    """Minute."""
    second: int
    """Second."""
    frame: int
    """Frame number."""
    is_ntsc: bool
    """Is NTSC."""
    is_pal: bool
    """Is PAL."""
    recordable: bool
    """Recordable."""
    tape_inserted: bool
    """Tape inserted."""
    vtr_mode: VTRMode
    """VTR mode."""
    @override
    @staticmethod
    def from_bytes(resp: bytes) -> VTRModeResponse:
        """Initialise from bytes."""
        parent = CommandResponse.from_bytes(resp)
        framerate = PAL_FRAMERATE if ((resp[5] >> 2) & 1) == 1 else NTSC_FRAMERATE
        return VTRModeResponse(parent.checksum,
                               parent.raw, parent.return_data, parent.status, parent.tuple,
                               bool(resp[5] & 1), framerate, resp[6], resp[7], resp[8], resp[9],
                               framerate == NTSC_FRAMERATE, framerate == PAL_FRAMERATE,
                               not bool(resp[4] >> 5 & 1), ((resp[4] >> 4) & 1) == 0,
                               VTRMode((resp[4]) & 0b1111))

    @override
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
    """Band information codes."""
    BROADCAST_SATELLITE = 0x40
    """Broadcast satellite."""
    TERRESTRIAL_BROADCAST = 0x30
    """Terrestrial broadcast."""


BANK_NUMBER_NONE = 0x51


@dataclass
class VTUModeResponse(CommandResponse):
    """VTR mode response information."""
    band_info: BandInfo
    """Band information."""
    bank_number: int | None
    """Bank number."""
    channel_number_by_bank: int | None
    """Channel number by bank."""
    channel_number_non_bank: int
    """Channel number non-bank."""
    real_channel: int
    """Non-preset channel number."""
    @staticmethod
    @override
    def from_bytes(resp: bytes) -> VTUModeResponse:
        parent = CommandResponse.from_bytes(resp)
        return VTUModeResponse(
            parent.checksum, parent.raw, parent.return_data, parent.status, parent.tuple,
            BandInfo(resp[4]), None if resp[5] == BANK_NUMBER_NONE else resp[6] - 100,
            None if resp[5] == BANK_NUMBER_NONE else resp[7], (resp[6] * 100) + resp[7], resp[5])

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


@dataclass
class PowerStateResponse(CommandResponse):
    """Power state response."""
    is_on: bool
    """If device is on."""
    @staticmethod
    @override
    def from_bytes(resp: bytes) -> PowerStateResponse:
        parent = CommandResponse.from_bytes(resp)
        return PowerStateResponse(parent.checksum, parent.raw, parent.return_data, parent.status,
                                  parent.tuple, bool(resp[4]))

    @override
    def __repr__(self) -> str:
        return ('<PowerStateResponse '
                f'checksum={hex(self.checksum)} '
                f'is_on={self.is_on} '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s}'
                '>')


@dataclass
class DeviceNameResponse(CommandResponse):
    """Device name response."""
    name: str
    """Device name."""
    @staticmethod
    @override
    def from_bytes(resp: bytes) -> DeviceNameResponse:
        """Initialise from bytes."""
        parent = CommandResponse.from_bytes(resp)
        return DeviceNameResponse(parent.checksum, parent.raw, parent.return_data, parent.status,
                                  parent.tuple, ''.join(chr(x) for x in parent.return_data[1:]))

    @override
    def __repr__(self) -> str:
        return ('<DeviceNameResponse '
                f'checksum={hex(self.checksum)} '
                f'name="{self.name}" '
                f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
                f'status={self.status!s}'
                '>')


def checksum(vals: Sequence[int]) -> int:
    """Checksum for JLIP commands."""
    sum_ = 0x80
    for i in range(10):
        sum_ -= (vals[i] & 0x7F)
    return sum_ & 0x7F


limiter = Limiter(Rate(2, Duration.SECOND))
fast_limiter = Limiter(Rate(10, Duration.SECOND))


class JLIP:  # noqa: PLR0904
    """
    Send commands to HR-S9600U VCRs and similar devices over JLIP.

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
        """
        Initialise the JLIP object.

        Parameters
        ----------
        serial_path : str
            Path to the serial port.
        jlip_id : int
            JLIP ID of the device.
        raise_on_error_response : bool
            If ``True``, raise an exception on error response.
        """
        self.comm = serial.Serial(serial_path, parity=serial.PARITY_ODD, rtscts=True, timeout=2)
        """Serial port object."""
        self.jlip_id = jlip_id
        """JLIP ID."""
        self.raise_on_error_response = raise_on_error_response
        """Raise on error response."""

    def send_command_base(self, *args: int) -> bytes:
        """
        Send a command (base method).

        Raises
        ------
        ValueError
            If the checksum does not match or if the command status is not accepted.
        """
        arr = (255, 255, self.jlip_id, *pad_right(0, args, 7))
        self.comm.write(bytearray([*arr, checksum(arr)]))
        sleep(0.1)
        ret = self.comm.read(11)
        actual_checksum = checksum(list(ret)[:10])
        if ret[10] != actual_checksum:
            msg = (f'Checksum did not match. Expected {actual_checksum} but received {ret[10]}.')
            raise ValueError(msg)
        status = ret[3] & 0b111
        if (self.raise_on_error_response and status not in {
                CommandStatus.COMMAND_ACCEPTED, CommandStatus.COMMAND_ACCEPTED_NOT_COMPLETE
        }):
            msg = f'Command status: {CommandStatus(status)!s}'
            raise ValueError(msg)
        return ret

    def send_command(self, *args: int) -> bytes:
        """
        Send a command at a slower rate limit.

        This will raise pyrate_limiter's :py:class:`pyrate_limiter.BucketFullException` if the rate
        limit is exceed.
        """
        limiter.try_acquire('command')
        return self.send_command_base(*args)

    def send_command_fast(self, *args: int) -> bytes:
        """
        Send a command with a faster rate limit.

        This will raise pyrate_limiter's :py:class:`pyrate_limiter.BucketFullException` if the rate
        limit is exceed.
        """
        fast_limiter.try_acquire('command_fast')
        return self.send_command_base(*args)

    def eject(self) -> CommandResponse:
        """Eject the tape."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x41, 0x60))

    def eject_wait(self) -> CommandResponse:
        """Eject the tape and wait until it is done."""
        resp = self.stop()
        sleep(0.5)
        resp = self.eject()
        while (resp := self.get_vtr_mode()).vtr_mode != VTRMode.EJECT:
            sleep(0.25)
        return resp

    def fast_forward(self) -> CommandResponse:
        """Fast forward the tape."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x44, 0x75))

    def fast_play_forward(self) -> CommandResponse:
        """Fast play forward."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x43, 0x21))

    def fast_play_backward(self) -> CommandResponse:
        """Fast play backward."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x43, 0x25))

    def frame_step(self) -> CommandResponse:
        """Move forward one frame."""
        return CommandResponse.from_bytes(self.send_command(0x48, 0x46, 0x75, 0x01))

    def frame_step_back(self) -> CommandResponse:
        """Move back one frame."""
        return CommandResponse.from_bytes(self.send_command(0x48, 0x46, 0x65, 0x01))

    def get_baud_rate_supported(self) -> CommandResponse:
        """
        Get the baud rate supported by the device.

        ``0x21`` is returned, meaning 19200 baud, but this cannot be trusted.
        """
        return CommandResponse.from_bytes(self.send_command(0x7C, 0x48, 0x20))

    def get_device_code(self) -> CommandResponse:
        """Get the device code."""
        return CommandResponse.from_bytes(self.send_command(0x7C, 0x49))

    def get_device_name(self) -> CommandResponse:
        """Get the device name."""
        return DeviceNameResponse.from_bytes(self.send_command(0x7C, 0x4C))

    def get_input(self) -> CommandResponse:
        """Get the input of the device."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x58, 0x20))

    def get_machine_code(self) -> CommandResponse:
        """Get the machine code."""
        return CommandResponse.from_bytes(self.send_command(0x7C, 0x45))

    def get_play_speed(self) -> CommandResponse:
        """
        Get playback speed.

        Known responses in the first data field:

        - ``0x67`` means playing backward quickly.
        - ``0x6D`` means paused or frame advancing.
        - ``0x75`` means normal.
        - ``0x77`` means playing forward quickly.
        - ``0x7F`` is returned when inapplicable.
        """
        return CommandResponse.from_bytes(self.send_command(0x48, 0x4E, 0x20))

    def get_power_state(self) -> PowerStateResponse:
        """Get the power state of the device."""
        return PowerStateResponse.from_bytes(self.send_command(0x3E, 0x4E, 0x20))

    def get_tuner_mode(self) -> VTUModeResponse:
        """Get the tuner mode."""
        return VTUModeResponse.from_bytes(self.send_command(0xA, 0x4E, 0x20))

    def get_vtr_mode(self, *, fast: bool = False) -> VTRModeResponse:
        """Get the VTR mode."""
        return VTRModeResponse.from_bytes(
            (self.send_command_fast if fast else self.send_command)(0x08, 0x4E, 0x20))

    def nop(self) -> CommandResponse:
        """No operation command."""
        return CommandResponse.from_bytes(self.send_command(0x7c, 0x4e, 0x20))

    def pause(self) -> CommandResponse:
        """Pause playback."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x43, 0x6d))

    def pause_recording(self) -> CommandResponse:
        """Pause recording."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x42, 0x6d))

    def play(self) -> CommandResponse:
        """Start playback."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x43, 0x75))

    def presence_check(self) -> CommandResponse:
        """Check if the device is present and responding."""
        return CommandResponse.from_bytes(self.send_command(0x7C, 0x4E, 0x20))

    def preset_channel_up(self) -> CommandResponse:
        """Change to the next preset channel."""
        return CommandResponse.from_bytes(self.send_command(0x0A, 0x44, 0x73, 0, 0, 0x7E))

    def preset_channel_down(self) -> CommandResponse:
        """Change to the previous preset channel."""
        return CommandResponse.from_bytes(self.send_command(0x0A, 0x44, 0x63, 0, 0, 0x7E))

    def real_channel_down(self) -> CommandResponse:
        """Change to the previous channel."""
        return CommandResponse.from_bytes(self.send_command(0x0A, 0x42, 0x63, 0, 0, 0x44))

    def real_channel_up(self) -> CommandResponse:
        """Change to the next channel."""
        return CommandResponse.from_bytes(self.send_command(0x0A, 0x42, 0x73, 0, 0, 0x44))

    def record(self) -> CommandResponse:
        """Start recording."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x42, 0x70))

    def reset_counter(self) -> CommandResponse:
        """Reset the timecode counter."""
        return CommandResponse.from_bytes(self.send_command(0x48, 0x4D, 0x20))

    def rewind(self) -> CommandResponse:
        """Rewind the tape."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x44, 0x65))

    def rewind_wait(self) -> CommandResponse:
        """Rewind the tape and wait until it is done."""
        resp = self.stop()
        sleep(1)
        resp = self.rewind()
        while (resp := self.get_vtr_mode()).vtr_mode == VTRMode.REW:
            sleep(1)
        return resp

    def set_channel(self, channel: int) -> CommandResponse:
        """Set the channel to a specific value."""
        return CommandResponse.from_bytes(self.send_command(0x0a, 0x44, 0x71, 0, channel, 0x7E))

    def set_jlip_id(self, n: int) -> CommandResponse:
        """
        Set the JLIP ID of the device.

        Raises
        ------
        ValueError
            If the ID is not between 1 and 99.
        """
        if n <= 0 or n > 99:  # noqa: PLR2004
            raise ValueError(n)
        self.jlip_id = n
        return CommandResponse.from_bytes(self.send_command(0x7C, 0x41, n))

    def set_input(self, n: int, nn: int) -> CommandResponse:
        """Set the input to a specific value."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x59, n, nn, 0x7F))

    def set_record_mode(self, n: int) -> CommandResponse:
        """Set the recording mode."""
        return CommandResponse.from_bytes(self.send_command(0x48, 0x43, n))

    def set_record_speed(self, n: int) -> CommandResponse:
        """Set the recording speed."""
        return CommandResponse.from_bytes(self.send_command(0x48, 0x42, n))

    def select_band(self, n: int) -> CommandResponse:
        """Select a band."""
        return CommandResponse.from_bytes(self.send_command(0x0A, 0x40, 0x71, n))

    def select_preset_channel(self, n: int, nn: int, nnn: int) -> CommandResponse:
        """Select a preset channel."""
        return CommandResponse.from_bytes(self.send_command(0x0A, 0x44, n, nn, nnn, 0x7E))

    def select_real_channel(self, n: int, nn: int, nnn: int) -> CommandResponse:
        """Select a channel."""
        return CommandResponse.from_bytes(self.send_command(0x0A, 0x42, n, nn, nnn, 0x44))

    def slow_play_backward(self) -> CommandResponse:
        """Slow play backward."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x43, 0x24))

    def slow_play_forward(self) -> CommandResponse:
        """Slow play forward."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x43, 0x20))

    def stop(self) -> CommandResponse:
        """Stop playback or recording."""
        return CommandResponse.from_bytes(self.send_command(0x08, 0x44, 0x60))

    def turn_off(self) -> CommandResponse:
        """Turn the device off."""
        return CommandResponse.from_bytes(self.send_command(0x3E, 0x40, 0x60))

    def turn_on(self) -> CommandResponse:
        """Turn the device on."""
        return CommandResponse.from_bytes(self.send_command(0x3E, 0x40, 0x70))

    @override
    def __repr__(self) -> str:
        return '<JLIP jlip_id={self.jlip_id} raise_on_error={self.raise_on_error_response}>'

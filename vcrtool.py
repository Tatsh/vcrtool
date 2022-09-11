from time import sleep
from typing import Any, NamedTuple, TypeVar
import enum

from pyrate_limiter import Duration, Limiter, RequestRate
import click
import serial

limiter = Limiter(RequestRate(10, Duration.SECOND))
T = TypeVar('T')


def checksum(vals: list[int]) -> int:
    sum_ = 0x80
    for i in range(10):
        sum_ -= (vals[i] & 0x7F)
    return sum_ & 0x7F


def pad_right(value: Any, list_: list[T], max_length: int) -> list[T]:
    if (diff := max_length - len(list_)) < 0:
        raise ValueError(diff)
    return list_ + (diff * [value])


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
        return (
            f'ResponseTuple(jlip_id={self.jlip_id}, '
            f'command_status={str(self.command_status)}, '
            f'return_data=[{", ".join(hex(n) for n in self.return_data[1:])}])'
        )


class CommandResponse:
    def __init__(self, resp: bytes):
        self.checksum = resp[10]
        self.raw = resp
        self.return_data = resp[3:10]
        self.status = CommandStatus(resp[3] & 0b111)
        self.tuple = ResponseTuple(resp[2], CommandStatus(resp[3] & 0b111),
                                   resp[4:10])

    def __repr__(self) -> str:
        return (
            '<CommandResponse '
            f'checksum={hex(self.checksum)} '
            f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
            f'status={str(self.status)}'
            '>')


class VTRMode(enum.IntEnum):
    EJECT = 0
    FF = 0b10
    NO_MODE = 0b1111
    PAUSE = 0b111
    PLAY_BWD = 0b110
    PLAY_FWD = 0b101
    REC = 0b1110
    REC_PAUSE = 0b1101
    REW = 0b11
    STOP = 1


class VTRModeResponse(CommandResponse):
    def __init__(self, resp: bytes):
        super().__init__(resp)
        self.drop_frame_mode_enabled = bool(resp[5] & 1)
        self.framerate = 25 if ((resp[5] >> 2) & 1) == 1 else 30
        self.hour, self.minute, self.second, self.frame = resp[6:10]
        self.is_ntsc = self.framerate == 30
        self.is_pal = self.framerate == 25
        self.recordable = not bool(resp[4] >> 5 & 1)
        self.tape_inserted = ((resp[4] >> 4) & 1) == 0
        self.vtr_mode = VTRMode((resp[4]) & 0b1111)

    def __repr__(self) -> str:
        return (
            '<VTRModeResponse '
            f'checksum={hex(self.checksum)} '
            f'counter="{self.hour:02}:{self.minute:02}:{self.second:02}:{self.frame:06}" '
            f'drop_framerate_mode_enabled={self.drop_frame_mode_enabled} '
            f'framerate={self.framerate} '
            f'is_ntsc={self.is_ntsc} '
            f'is_pal={self.is_pal} '
            f'recordable={self.recordable} '
            f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
            f'status={str(self.status)} '
            f'tape_inserted={self.tape_inserted} '
            f'vtr_mode={str(self.vtr_mode)}'
            '>')


class BandInfo(enum.IntEnum):
    BROADCAST_SATELLITE = 0x40
    TERRESTRIAL_BROADCAST = 0x30


class VTUModeResponse(CommandResponse):
    def __init__(self, resp: bytes):
        super().__init__(resp)
        self.band_info = BandInfo(resp[4])
        self.bank_number = None if resp[5] == 0x51 else resp[6] - 100
        self.channel_number_by_bank = None if resp[5] == 0x51 else resp[7]
        self.channel_number_non_bank = (resp[6] * 100) + resp[7]
        self.real_channel = resp[5]

    def __repr__(self) -> str:
        return (
            '<VTUModeResponse '
            f'band_info={str(self.band_info)} '
            f'bank_number={str(self.bank_number)} '
            f'channel_number_by_bank={self.channel_number_by_bank} '
            f'channel_number_non_bank={self.channel_number_non_bank} '
            f'checksum={hex(self.checksum)} '
            f'real_channel={self.real_channel} '
            f'return_data=[{", ".join(f"0x{n:02x}" for n in self.return_data[1:])}] '
            f'status={str(self.status)}'
            '>')


class PowerStateResponse(CommandResponse):
    def __init__(self, resp: bytes):
        super().__init__(resp)
        self.is_on = bool(resp[4])


class JLIPHRSeriesVCR:
    """Class to run commands against HR-S9600U and similar VCRs over JLIP.

    References:

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
                 raise_on_error_response: bool = True):
        self._ser = serial.Serial(serial_path,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_ODD,
                                  rtscts=True,
                                  stopbits=serial.STOPBITS_ONE,
                                  timeout=2)
        self.jlip_id = jlip_id
        self._raise = raise_on_error_response
        self._tuner_info = self.get_tuner_mode()

    @limiter.ratelimit('serial', delay=True)
    def send_command(self, *args: Any) -> bytes:
        arr = [0xFF, 0xFF, self.jlip_id] + pad_right(0, list(args), 7)
        self._ser.write(arr + [checksum(arr)])
        sleep(0.1)
        ret = self._ser.read(11)
        actual_checksum = checksum(list(x for x in ret)[:10])
        if ret[10] != actual_checksum:
            raise ValueError(
                f'Checksum did not match. Expected {actual_checksum} but '
                f'received {ret[10]}')
        if (self._raise and (ret[3] & 0b111)
                not in (CommandStatus.COMMAND_ACCEPTED,
                        CommandStatus.COMMAND_ACCEPTED_NOT_COMPLETE)):
            raise ValueError(f'Command status: {ret[3]}')
        return ret

    def eject(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x41, 0x60))

    def fast_forward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x44, 0x75))

    def fast_play_forward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x21))

    def fast_play_backward(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x25))

    def get_input(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x08, 0x43, 0x21))

    def get_play_speed(self) -> CommandResponse:
        return CommandResponse(self.send_command(0x48, 0x4E, 0x20))

    def get_power_state(self) -> PowerStateResponse:
        return PowerStateResponse(self.send_command(0x3E, 0x4E, 0x20))

    def get_tuner_mode(self) -> VTUModeResponse:
        return VTUModeResponse(self.send_command(0xA, 0x4E, 0x20))

    def get_vtr_mode(self) -> VTRModeResponse:
        return VTRModeResponse(self.send_command(0x08, 0x4E, 0x20))

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
        resp = self.rewind()
        while (resp := self.get_vtr_mode()).vtr_mode != VTRMode.STOP:
            sleep(1)
        return resp

    def set_channel(self, channel: int):
        return CommandResponse(
            self.send_command(0x0a, 0x44, 0x71, 0, channel, 0x7E))

    def set_input(self, n: int, nn: int):
        return CommandResponse(self.send_command(0x08, 0x59, n, nn, 0x7F))

    def set_record_mode(self, n: int):
        return CommandResponse(self.send_command(0x48, 0x43, n))

    def set_record_speed(self, n: int):
        return CommandResponse(self.send_command(0x48, 0x42, n))

    def select_band(self, n: int):
        return CommandResponse(self.send_command(0x0A, 0x40, 0x71, n))

    def select_preset_channel(self, n: int, nn: int, nnn: int):
        return CommandResponse(self.send_command(0x0A, 0x44, n, nn, nnn, 0x7E))

    def select_real_channel(self, n: int, nn: int, nnn: int):
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

    def __repr__(self) -> str:
        return ('<JLIPHRSeriesVCR '
                f'jlip_id={self.jlip_id} '
                f'raise_on_error={self._raise}'
                f'tuner_info={self._tuner_info}'
                '>')


@click.command()
@click.argument('serial_device')
@click.argument('commands', nargs=-1)
def main(serial_device: str, commands: list[str]) -> None:
    vcr = JLIPHRSeriesVCR(serial_device, raise_on_error_response=False)
    disallowed = ('send_command',)
    for command in (
            x for x in commands
            if x not in disallowed and getattr(vcr, x, None) is not None):
        print(getattr(vcr, command)())

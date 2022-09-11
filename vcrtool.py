from time import sleep
from typing import Any, TypeVar
import enum
import reprlib

import click
import serial

T = TypeVar('T')
WAIT_TIME = 0.1  # seconds


def checksum(vals: list[int]) -> int:
    sum_ = 0x80
    for i in range(10):
        sum_ -= (vals[i] & 0x7F)
    return sum_ & 0x7F


def pad_right(value: Any, list_: list[T], max_length: int) -> list[T]:
    if (diff := max_length - len(list_)) < 0:
        raise ValueError()
    return list_ + (diff * [value])


class CommandStatus(enum.IntEnum):
    COMMAND_NOT_IMPLEMENTED = 1
    COMMAND_ACCEPTED = 3
    COMMAND_ACCEPTED_NOT_COMPLETE = 4
    COMMAND_NOT_POSSIBLE = 5


class PowerMode(enum.IntEnum):
    ON = 1
    OFF = 0


class CommandResponse:
    def __init__(self, resp: bytes):
        self.raw = resp
        self.status = CommandStatus(resp[3])
        self.return_data = resp[3:10]
        self.checksum = resp[10]


class TapeState(enum.IntEnum):
    NO_TAPE = 1
    TAPE_INSERTED = 0


class VTRMode(enum.IntEnum):
    EJECT = 0
    STOP = 1
    FF = 0b10
    REW = 0b11
    PLAY_FWD = 0b101
    PLAY_BWD = 0b110
    PAUSE = 0b111
    REC_PAUSE = 0b1101
    REC = 0b1110
    NO_MODE = 0b1111


class VTRModeResponse(CommandResponse):
    def __init__(self, resp: bytes):
        super().__init__(resp)
        self.recordable = not bool(resp[4] >> 5 & 1)
        self.tape_state = TapeState((resp[4] >> 4) & 1)
        self.vtr_mode = VTRMode((resp[4]) & 0b1111)
        self.framerate = 25 if ((resp[5] >> 2) & 1) == 1 else 30
        self.drop_frame_mode_enabled = bool(resp[5] & 1)
        self.hour, self.minute, self.second, self.frame = resp[6:10]

    def __repr__(self):
        return (
            '<VTRModeResponse '
            f'counter="{self.hour:02}:{self.minute:02}:{self.second:02}:{self.frame:06}" '
            f'drop_framerate_mode_enabled={self.drop_frame_mode_enabled} '
            f'framerate={self.framerate} '
            f'recordable={self.recordable} '
            f'tape_state={str(self.tape_state)} vtr_mode={str(self.vtr_mode)}'
            '>')


class JLIPHRSeriesVCR:
    """Class to run commands against HR-S9600U and similar VCRs over JLIP."""
    def __init__(self,
                 serial_path: str,
                 jlip_id: int = 1,
                 raise_on_error_response: bool = True):
        self._ser = serial.Serial(serial_path,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_ODD,
                                  rtscts=True,
                                  timeout=2,
                                  stopbits=serial.STOPBITS_ONE)
        self._jlip_id = jlip_id
        self._raise = raise_on_error_response

    def send_command(self, *args: Any) -> bytes:
        arr = [0xFF, 0xFF, self._jlip_id] + pad_right(0, list(args), 7)
        self._ser.write(arr + [checksum(arr)])
        sleep(WAIT_TIME)
        ret = self._ser.read(11)
        received_checksum = ret[10]
        actual_checksum = checksum([x for x in ret][:10])
        if received_checksum != received_checksum:
            raise ValueError(
                f'Checksum did not match. Expected {actual_checksum} but '
                f'received {received_checksum}')
        if (self._raise and (ret[3] & 0b111)
                not in (CommandStatus.COMMAND_ACCEPTED,
                        CommandStatus.COMMAND_ACCEPTED_NOT_COMPLETE)):
            raise ValueError(f'Command status: {ret[3]}')
        return ret

    def play(self):
        return self.send_command(0x08, 0x43, 0x75)

    def stop(self):
        return self.send_command(0x08, 0x44, 0x60)

    def pause(self):
        return self.send_command(0x08, 0x43, 0x6d)

    def fast_forward(self):
        return self.send_command(0x08, 0x44, 0x75)

    def rewind(self):
        return self.send_command(0x08, 0x44, 0x65)

    def eject(self):
        return self.send_command(0x08, 0x41, 0x60)

    def fast_play_forward(self):
        return self.send_command(0x08, 0x43, 0x21)

    def fast_play_backward(self):
        self.send_command(0x08, 0x43, 0x25)

    def slow_play_forward(self):
        return self.send_command(0x08, 0x43, 0x20)

    def slow_play_backward(self):
        return self.send_command(0x08, 0x43, 0x24)

    def record(self):
        return self.send_command(0x08, 0x42, 0x70)

    def pause_recording(self):
        return self.send_command(0x08, 0x42, 0x6d)

    def get_input(self):
        return self.send_command(0x08, 0x43, 0x21)

    def set_input(self, n: int, nn: int):
        return self.send_command(0x08, 0x59, n, nn, 0x7F)

    def reset_counter(self):
        return self.send_command(0x48, 0x4D, 0x20)

    def set_channel(self, channel: int):
        return self.send_command(0x0a, 0x44, 0x71, 0, channel, 0x7e)

    def nop(self):
        return self.send_command(0x7c, 0x4e, 0x20)

    def get_power_mode(self):
        return self.send_command(0x3E, 0x4E, 0x20)

    def turn_on(self):
        return self.send_command(0x3E, 0x40, 0x70)

    def turn_off(self):
        return self.send_command(0x3E, 0x40, 0x60)

    def get_tuner_mode(self):
        return self.send_command(0xA, 0x4E, 0x20)

    def get_vtr_mode(self):
        return VTRModeResponse(self.send_command(0x08, 0x4E, 0x20))

    def get_play_speed(self):
        return self.send_command(0x48, 0x4E, 0x20)

    def set_record_speed(self, n: int):
        return self.send_command(0x48, 0x42, n)

    def set_record_mode(self, n: int):
        return self.send_command(0x48, 0x43, n)

    def select_band(self, n: int):
        return self.send_command(0xA, 0x40, 0x71, n)

    def select_real_channel(self, n: int, nn: int, nnn: int):
        return self.send_command(0xA, 0x42, n, nn, nnn, 0x44)

    def select_preset_channel(self, n: int, nn: int, nnn: int):
        return self.send_command(0xA, 0x44, n, nn, nnn, 0x7E)

    def channel_up(self):
        return self.send_command(0x73)

    def channel_down(self):
        return self.send_command(0x63)


@click.command()
@click.argument('serial_device')
def main(serial_device: str) -> None:
    vcr = JLIPHRSeriesVCR(serial_device)
    print(vcr.turn_off())

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock
import sys

from vcrtool.jlip import (
    JLIP,
    NTSC_FRAMERATE,
    BandInfo,
    CommandResponse,
    CommandResponseTuple,
    CommandStatus,
    DeviceNameResponse,
    PowerStateResponse,
    VTRMode,
    VTRModeResponse,
    VTUModeResponse,
    checksum,
)
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def mock_serial(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('serial.Serial')


@pytest.fixture
def jlip(mock_serial: MagicMock) -> JLIP:
    return JLIP(serial_path='/dev/ttyS0')


def test_eject(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.eject()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x41, 0x60)


def test_get_power_state(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.PowerStateResponse', mock_response)
    response = jlip.get_power_state()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x3E, 0x4E, 0x20)


def test_get_device_name(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.DeviceNameResponse', mock_response)
    response = jlip.get_device_name()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x7C, 0x4C)


def test_get_vtr_mode(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.VTRModeResponse', mock_response)
    response = jlip.get_vtr_mode()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x4E, 0x20)


def test_set_jlip_id_invalid(jlip: MagicMock) -> None:
    with pytest.raises(ValueError, match='0'):
        jlip.set_jlip_id(0)


def test_set_jlip_id_valid(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.set_jlip_id(10)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x7C, 0x41, 10)


def test_turn_on(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.turn_on()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x3E, 0x40, 0x70)


def test_turn_off(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.turn_off()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x3E, 0x40, 0x60)


def test_fast_forward(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.fast_forward()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x44, 0x75)


def test_rewind(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.rewind()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x44, 0x65)


def test_pause(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.pause()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x43, 0x6d)


def test_play(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.play()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x43, 0x75)


def test_record(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.record()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x42, 0x70)


def test_stop(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.stop()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x44, 0x60)


def test_set_channel(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.set_channel(5)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0a, 0x44, 0x71, 0, 5, 0x7E)


def test_set_record_mode(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.set_record_mode(3)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x48, 0x43, 3)


def test_set_record_speed(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.set_record_speed(2)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x48, 0x42, 2)


def test_eject_wait(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.jlip.sleep')
    mocker.patch.object(jlip, 'stop', return_value=MagicMock())
    mocker.patch.object(jlip, 'eject', return_value=MagicMock())
    mock_get_vtr_mode = mocker.patch.object(
        jlip,
        'get_vtr_mode',
        side_effect=[MagicMock(vtr_mode=VTRMode.STOP),
                     MagicMock(vtr_mode=VTRMode.EJECT)])
    response = jlip.eject_wait()
    assert response.vtr_mode == VTRMode.EJECT
    jlip.stop.assert_called_once()
    jlip.eject.assert_called_once()
    assert mock_get_vtr_mode.call_count == 2


def test_rewind_wait(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.jlip.sleep')
    mocker.patch.object(jlip, 'stop', return_value=MagicMock())
    mocker.patch.object(jlip, 'rewind', return_value=MagicMock())
    mock_get_vtr_mode = mocker.patch.object(
        jlip,
        'get_vtr_mode',
        side_effect=[MagicMock(vtr_mode=VTRMode.REW),
                     MagicMock(vtr_mode=VTRMode.STOP)])
    response = jlip.rewind_wait()
    assert response.vtr_mode == VTRMode.STOP
    jlip.stop.assert_called_once()
    jlip.rewind.assert_called_once()
    assert mock_get_vtr_mode.call_count == 2


def test_fast_play_forward(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.fast_play_forward()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x43, 0x21)


def test_fast_play_backward(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.fast_play_backward()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x43, 0x25)


def test_frame_step(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.frame_step()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x48, 0x46, 0x75, 0x01)


def test_frame_step_back(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.frame_step_back()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x48, 0x46, 0x65, 0x01)


def test_get_baud_rate_supported(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.get_baud_rate_supported()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x7C, 0x48, 0x20)


def test_get_device_code(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.get_device_code()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x7C, 0x49)


def test_get_machine_code(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.get_machine_code()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x7C, 0x45)


def test_get_play_speed(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.get_play_speed()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x48, 0x4E, 0x20)


def test_checksum_valid(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.jlip.pad_right', side_effect=lambda _, y, __: y)
    vals = [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0]
    result = checksum(vals)
    expected = (0x80 - sum(v & 0x7F for v in vals)) & 0x7F
    assert result == expected


def test_checksum_all_zeros(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.jlip.pad_right', side_effect=lambda _, y, __: y)
    vals = [0] * 10
    result = checksum(vals)
    expected = 0x80 & 0x7F
    assert result == expected


def test_checksum_large_values(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.jlip.pad_right', side_effect=lambda _, y, __: y)
    vals = [0xFF] * 10
    result = checksum(vals)
    expected = (0x80 - sum(v & 0x7F for v in vals)) & 0x7F
    assert result == expected


def test_send_command_base_valid_checksum(jlip: MagicMock, mocker: MockerFixture) -> None:
    mock_serial_write = mocker.patch.object(jlip.comm, 'write')
    mock_serial_read = mocker.patch.object(
        jlip.comm, 'read', return_value=b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C')
    mock_checksum = mocker.patch('vcrtool.jlip.checksum', side_effect=lambda _: 0x7C)
    response = jlip.send_command_base(0x01, 0x02, 0x03)
    mock_serial_write.assert_called_once_with(bytearray([255, 255, 1, 1, 2, 3, 0, 0, 0, 0, 124]))
    mock_serial_read.assert_called_once_with(11)
    mock_checksum.assert_called_with([255, 255, 1, 3, 0, 0, 0, 0, 0, 0])
    assert response == b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C'


def test_send_command_base_invalid_checksum(jlip: MagicMock, mocker: MockerFixture) -> None:
    mock_serial_write = mocker.patch.object(jlip.comm, 'write')
    mock_serial_read = mocker.patch.object(
        jlip.comm, 'read', return_value=b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7D')
    mock_checksum = mocker.patch('vcrtool.jlip.checksum', side_effect=lambda _: 0x7C)

    with pytest.raises(ValueError,
                       match=r'Checksum did not match\. Expected 124 but received 125\.'):
        jlip.send_command_base(0x01, 0x02, 0x03)

    mock_serial_write.assert_called_once_with(bytearray([255, 255, 1, 1, 2, 3, 0, 0, 0, 0, 124]))
    mock_serial_read.assert_called_once_with(11)
    mock_checksum.assert_called_with([255, 255, 1, 3, 0, 0, 0, 0, 0, 0])


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_send_command_base_invalid_status(jlip: MagicMock, mocker: MockerFixture) -> None:
    mock_serial_write = mocker.patch.object(jlip.comm, 'write')
    mock_serial_read = mocker.patch.object(
        jlip.comm, 'read', return_value=b'\xFF\xFF\x01\x05\x00\x00\x00\x00\x00\x00\x7C')
    mock_checksum = mocker.patch('vcrtool.jlip.checksum', side_effect=lambda _: 0x7C)

    with pytest.raises(ValueError, match='Command status: 5'):
        jlip.send_command_base(0x01, 0x02, 0x03)

    mock_serial_write.assert_called_once_with(bytearray([255, 255, 1, 1, 2, 3, 0, 0, 0, 0, 124]))
    mock_serial_read.assert_called_once_with(11)
    mock_checksum.assert_called_with([255, 255, 1, 5, 0, 0, 0, 0, 0, 0])


def test_send_command_base_status_not_raised(jlip: MagicMock, mocker: MockerFixture) -> None:
    jlip.raise_on_error_response = False
    mock_serial_write = mocker.patch.object(jlip.comm, 'write')
    mock_serial_read = mocker.patch.object(
        jlip.comm, 'read', return_value=b'\xFF\xFF\x01\x05\x00\x00\x00\x00\x00\x00\x7C')
    mock_checksum = mocker.patch('vcrtool.jlip.checksum', side_effect=lambda _: 0x7C)

    response = jlip.send_command_base(0x01, 0x02, 0x03)

    mock_serial_write.assert_called_once_with(bytearray([255, 255, 1, 1, 2, 3, 0, 0, 0, 0, 124]))
    mock_serial_read.assert_called_once_with(11)
    mock_checksum.assert_called_with([255, 255, 1, 5, 0, 0, 0, 0, 0, 0])
    assert response == b'\xFF\xFF\x01\x05\x00\x00\x00\x00\x00\x00\x7C'


def test_get_input(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.get_input()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x58, 0x20)


def test_get_tuner_mode(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.VTUModeResponse', mock_response)
    response = jlip.get_tuner_mode()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0A, 0x4E, 0x20)


def test_nop(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.nop()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x7C, 0x4E, 0x20)


def test_pause_recording(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.pause_recording()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x42, 0x6d)


def test_select_band(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.select_band(3)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0A, 0x40, 0x71, 3)


def test_select_preset_channel(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.select_preset_channel(1, 2, 3)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0A, 0x44, 1, 2, 3, 0x7E)


def test_select_real_channel(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.select_real_channel(1, 2, 3)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0A, 0x42, 1, 2, 3, 0x44)


def test_slow_play_backward(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.slow_play_backward()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x43, 0x24)


def test_slow_play_forward(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.slow_play_forward()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x43, 0x20)


def test_reset_counter(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.reset_counter()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x48, 0x4D, 0x20)


def test_presence_check(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.presence_check()
    assert response == mock_response

    jlip.send_command.assert_called_once_with(0x7C, 0x4E, 0x20)


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_command_response_tuple_repr() -> None:
    response_tuple = CommandResponseTuple(jlip_id=1,
                                          command_status=CommandStatus.COMMAND_ACCEPTED,
                                          return_data=b'\x01\x02\x03')
    expected_repr = ('<CommandResponseTuple jlip_id=1, '
                     'command_status=3, '
                     'return_data=[0x2, 0x3]>')
    assert repr(response_tuple) == expected_repr


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_command_response_repr() -> None:
    response = CommandResponse(checksum=0x7C,
                               raw=b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C',
                               return_data=b'\x03\x00\x00\x00\x00\x00\x00',
                               status=CommandStatus.COMMAND_ACCEPTED,
                               tuple=CommandResponseTuple(
                                   jlip_id=1,
                                   command_status=CommandStatus.COMMAND_ACCEPTED,
                                   return_data=b'\x00\x00\x00\x00\x00\x00'))
    expected_repr = ('<CommandResponse checksum=0x7c '
                     'return_data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00] '
                     'status=3>')
    assert repr(response) == expected_repr


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_vtr_mode_response_repr() -> None:
    response = VTRModeResponse(checksum=0x7C,
                               raw=b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C',
                               return_data=b'\x03\x00\x00\x00\x00\x00\x00',
                               status=CommandStatus.COMMAND_ACCEPTED,
                               tuple=CommandResponseTuple(
                                   jlip_id=1,
                                   command_status=CommandStatus.COMMAND_ACCEPTED,
                                   return_data=b'\x00\x00\x00\x00\x00\x00'),
                               drop_frame_mode_enabled=True,
                               framerate=30,
                               hour=1,
                               minute=2,
                               second=3,
                               frame=4,
                               is_ntsc=True,
                               is_pal=False,
                               recordable=True,
                               tape_inserted=True,
                               vtr_mode=VTRMode.PLAY_FWD)
    expected_repr = ('<VTRModeResponse checksum=0x7c '
                     'counter="01:02:03:000004" '
                     'drop_framerate_mode_enabled=True '
                     'framerate=30 '
                     'is_ntsc=True '
                     'is_pal=False '
                     'recordable=True '
                     'return_data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00] '
                     'status=3 '
                     'tape_inserted=True '
                     'vtr_mode=6>')
    assert repr(response) == expected_repr


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_vtu_mode_response_repr() -> None:
    response = VTUModeResponse(checksum=0x7C,
                               raw=b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C',
                               return_data=b'\x03\x00\x00\x00\x00\x00\x00',
                               status=CommandStatus.COMMAND_ACCEPTED,
                               tuple=CommandResponseTuple(
                                   jlip_id=1,
                                   command_status=CommandStatus.COMMAND_ACCEPTED,
                                   return_data=b'\x00\x00\x00\x00\x00\x00'),
                               band_info=BandInfo.TERRESTRIAL_BROADCAST,
                               bank_number=None,
                               channel_number_by_bank=None,
                               channel_number_non_bank=5,
                               real_channel=105)
    expected_repr = ('<VTUModeResponse band_info=48 '
                     'bank_number=None '
                     'channel_number_by_bank=None '
                     'channel_number_non_bank=5 '
                     'checksum=0x7c '
                     'real_channel=105 '
                     'return_data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00] '
                     'status=3>')
    assert repr(response) == expected_repr


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_power_state_response_repr() -> None:
    response = PowerStateResponse(checksum=0x7C,
                                  raw=b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C',
                                  return_data=b'\x03\x00\x00\x00\x00\x00\x00',
                                  status=CommandStatus.COMMAND_ACCEPTED,
                                  tuple=CommandResponseTuple(
                                      jlip_id=1,
                                      command_status=CommandStatus.COMMAND_ACCEPTED,
                                      return_data=b'\x00\x00\x00\x00\x00\x00'),
                                  is_on=True)
    expected_repr = ('<PowerStateResponse checksum=0x7c '
                     'is_on=True '
                     'return_data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00] '
                     'status=3>')
    assert repr(response) == expected_repr


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_device_name_response_repr() -> None:
    response = DeviceNameResponse(checksum=0x7C,
                                  raw=b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C',
                                  return_data=b'\x03\x00\x00\x00\x00\x00\x00',
                                  status=CommandStatus.COMMAND_ACCEPTED,
                                  tuple=CommandResponseTuple(
                                      jlip_id=1,
                                      command_status=CommandStatus.COMMAND_ACCEPTED,
                                      return_data=b'\x00\x00\x00\x00\x00\x00'),
                                  name='TestDevice')
    expected_repr = ('<DeviceNameResponse checksum=0x7c '
                     'name="TestDevice" '
                     'return_data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00] '
                     'status=3>')
    assert repr(response) == expected_repr


@pytest.mark.skipif(sys.version_info < (3, 11), reason='Requires Python 3.11.')
def test_jlip_repr(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.jlip.serial.Serial')
    jlip = JLIP(serial_path='/dev/ttyS0', jlip_id=1, raise_on_error_response=True)
    expected_repr = '<JLIP jlip_id={self.jlip_id} raise_on_error={self.raise_on_error_response}>'
    assert repr(jlip) == expected_repr


def test_set_input_valid(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.set_input(1, 2)
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x08, 0x59, 1, 2, 0x7F)


def test_preset_channel_up(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.preset_channel_up()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0A, 0x44, 0x73, 0, 0, 0x7E)


def test_preset_channel_down(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.preset_channel_down()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0A, 0x44, 0x63, 0, 0, 0x7E)


def test_real_channel_up(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.real_channel_up()
    assert response == mock_response
    jlip.send_command.assert_called_once_with(0x0A, 0x42, 0x73, 0, 0, 0x44)


def test_real_channel_down(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command', return_value=b'\x00' * 11)
    mock_response = MagicMock()
    mock_response.from_bytes.return_value = mock_response
    mocker.patch('vcrtool.jlip.CommandResponse', mock_response)
    response = jlip.real_channel_down()
    assert response == mock_response


def test_send_command(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command_base', return_value=b'\x00' * 11)
    mock_limiter = mocker.patch('vcrtool.jlip.limiter.try_acquire')
    response = jlip.send_command(0x01, 0x02, 0x03)
    assert response == b'\x00' * 11
    mock_limiter.assert_called_once_with('command')
    jlip.send_command_base.assert_called_once_with(0x01, 0x02, 0x03)


def test_send_command_fast(jlip: MagicMock, mocker: MockerFixture) -> None:
    mocker.patch.object(jlip, 'send_command_base', return_value=b'\x00' * 11)
    mock_fast_limiter = mocker.patch('vcrtool.jlip.fast_limiter.try_acquire')
    response = jlip.send_command_fast(0x01, 0x02, 0x03)
    assert response == b'\x00' * 11
    mock_fast_limiter.assert_called_once_with('command_fast')
    jlip.send_command_base.assert_called_once_with(0x01, 0x02, 0x03)


def test_command_response_from_bytes(mocker: MockerFixture) -> None:
    raw_data = b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C'
    response = CommandResponse.from_bytes(raw_data)
    assert response.checksum == 0x7C
    assert response.raw == raw_data
    assert response.return_data == b'\x03\x00\x00\x00\x00\x00\x00'
    assert response.status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.jlip_id == 1
    assert response.tuple.command_status == CommandStatus.COMMAND_ACCEPTED


def test_vtu_mode_response_from_bytes() -> None:
    raw_data = b'\xFF\xFF\x01\x03\x30\x00\x00\x00\x00\x05\x7C'
    response = VTUModeResponse.from_bytes(raw_data)
    assert response.checksum == 0x7C
    assert response.raw == raw_data
    assert response.return_data == b'\x030\x00\x00\x00\x00\x05'
    assert response.status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.jlip_id == 1
    assert response.tuple.command_status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.return_data == b'\x30\x00\x00\x00\x00\x05'
    assert response.band_info == BandInfo.TERRESTRIAL_BROADCAST
    assert response.bank_number == -100
    assert response.channel_number_by_bank == 0
    assert response.channel_number_non_bank == 0
    assert response.real_channel == 0


def test_vtr_mode_response_from_bytes(mocker: MockerFixture) -> None:
    raw_data = b'\xFF\xFF\x01\x03\x00\x00\x00\x00\x00\x00\x7C'
    response = VTRModeResponse.from_bytes(raw_data)
    assert response.checksum == 0x7C
    assert response.raw == raw_data
    assert response.return_data == b'\x03\x00\x00\x00\x00\x00\x00'
    assert response.status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.jlip_id == 1
    assert response.tuple.command_status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.return_data == b'\x00\x00\x00\x00\x00\x00'
    assert response.drop_frame_mode_enabled is False
    assert response.framerate == NTSC_FRAMERATE
    assert response.hour == 0
    assert response.minute == 0
    assert response.second == 0
    assert response.frame == 0
    assert response.is_ntsc is True
    assert response.is_pal is False
    assert response.recordable is True
    assert response.tape_inserted is True
    assert response.vtr_mode == VTRMode.EJECT


def test_power_state_response_from_bytes() -> None:
    raw_data = b'\xFF\xFF\x01\x03\x01\x00\x00\x00\x00\x00\x7C'
    response = PowerStateResponse.from_bytes(raw_data)
    assert response.checksum == 0x7C
    assert response.raw == raw_data
    assert response.return_data == b'\x03\x01\x00\x00\x00\x00\x00'
    assert response.status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.jlip_id == 1
    assert response.tuple.command_status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.return_data == b'\x01\x00\x00\x00\x00\x00'
    assert response.is_on is True


def test_device_name_response_from_bytes() -> None:
    raw_data = b'\xFF\xFF\x01\x03\x54\x65\x73\x74\x44\x65\x7C'
    response = DeviceNameResponse.from_bytes(raw_data)
    assert response.checksum == 0x7C
    assert response.raw == raw_data
    assert response.return_data == b'\x03\x54\x65\x73\x74\x44\x65'
    assert response.status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.jlip_id == 1
    assert response.tuple.command_status == CommandStatus.COMMAND_ACCEPTED
    assert response.tuple.return_data == b'\x54\x65\x73\x74\x44\x65'
    assert response.name == 'TestDe'

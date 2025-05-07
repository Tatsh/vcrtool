from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

from vcrtool.capture_stereo import VTRMode, _a_main, main  # noqa: PLC2701
import click
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_a_main_success(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.adebug_sleep', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.psutil.pid_exists', side_effect=[True, False])
    mocker.patch('vcrtool.capture_stereo.Path.unlink')
    mocker.patch('vcrtool.capture_stereo.Path.stem', return_value='output_base')
    mock_v4l2_ctl_proc = AsyncMock()
    mock_v4l2_ctl_proc.pid = 1234
    mock_v4l2_ctl_proc.returncode = 0
    mock_v4l2_ctl_proc.wait = AsyncMock(return_value=0)
    mock_ffmpeg_proc = AsyncMock()
    mock_ffmpeg_proc.pid = 1234
    mock_ffmpeg_proc.wait = AsyncMock(return_value=0)
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec',
                 side_effect=[mock_ffmpeg_proc, mock_v4l2_ctl_proc])
    mock_vcr = MagicMock()
    mock_vcr.get_vtr_mode.return_value = MagicMock(vtr_mode=VTRMode.PLAY_FWD)
    result = await _a_main(video_device='video_device',
                           audio_device='audio_device',
                           length=10,
                           output='output',
                           input_index=1,
                           vbi_device=None,
                           vcr=mock_vcr)
    assert result == 0
    mock_vcr.reset_counter.assert_called_once()
    mock_vcr.play.assert_called_once()
    mock_ffmpeg_proc.terminate.assert_not_called()


@pytest.mark.asyncio
async def test_a_main_vbi_device(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.adebug_sleep', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.psutil.pid_exists', side_effect=[False, True])
    mocker.patch('vcrtool.capture_stereo.Path.unlink')
    mocker.patch('vcrtool.capture_stereo.Path.stem', return_value='output_base')
    mock_v4l2_ctl_proc = AsyncMock()
    mock_v4l2_ctl_proc.pid = 1234
    mock_v4l2_ctl_proc.returncode = 0
    mock_v4l2_ctl_proc.wait = AsyncMock(return_value=0)
    mock_ffmpeg_proc = AsyncMock()
    mock_ffmpeg_proc.pid = 1234
    mock_ffmpeg_proc.wait = AsyncMock(return_value=0)
    mock_vbi_proc = AsyncMock()
    mock_vbi_proc.wait = AsyncMock(return_value=0)
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec',
                 side_effect=[mock_ffmpeg_proc, mock_vbi_proc, mock_v4l2_ctl_proc])
    mock_vcr = MagicMock()
    mock_vcr.get_vtr_mode.return_value = MagicMock(vtr_mode=VTRMode.PLAY_FWD)
    result = await _a_main(video_device='video_device',
                           audio_device='audio_device',
                           length=10,
                           output='output',
                           input_index=1,
                           vbi_device='vbi_device',
                           vcr=mock_vcr)

    assert result == 0
    mock_vbi_proc.terminate.assert_called_once()


@pytest.mark.asyncio
async def test_a_main_vcr_not_playing(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.adebug_sleep', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.psutil.pid_exists', side_effect=[True, False])
    mocker.patch('vcrtool.capture_stereo.Path.unlink')
    mocker.patch('vcrtool.capture_stereo.Path.stem', return_value='output_base')
    mock_v4l2_ctl_proc = AsyncMock()
    mock_v4l2_ctl_proc.pid = 1234
    mock_v4l2_ctl_proc.returncode = 0
    mock_v4l2_ctl_proc.wait = AsyncMock(return_value=0)
    mock_ffmpeg_proc = AsyncMock()
    mock_ffmpeg_proc.pid = 1234
    mock_ffmpeg_proc.wait = AsyncMock(return_value=0)
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec',
                 side_effect=[mock_ffmpeg_proc, mock_v4l2_ctl_proc])
    mock_vcr = MagicMock()
    mock_vcr.get_vtr_mode.return_value = MagicMock(vtr_mode=VTRMode.STOP)
    result = await _a_main(video_device='video_device',
                           audio_device='audio_device',
                           length=10,
                           output='output',
                           input_index=1,
                           vbi_device=None,
                           vcr=mock_vcr)
    assert result == 0
    mock_ffmpeg_proc.terminate.assert_called_once()


@pytest.mark.asyncio
async def test_a_main_ffmpeg_error(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.adebug_sleep', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.psutil.pid_exists', side_effect=[True, False])
    mocker.patch('vcrtool.capture_stereo.Path.unlink')
    mocker.patch('vcrtool.capture_stereo.Path.stem', return_value='output_base')
    mock_v4l2_ctl_proc = AsyncMock()
    mock_v4l2_ctl_proc.pid = 1234
    mock_v4l2_ctl_proc.returncode = 0
    mock_v4l2_ctl_proc.wait = AsyncMock(return_value=0)
    mock_ffmpeg_proc = AsyncMock()
    mock_ffmpeg_proc.pid = 1234
    mock_ffmpeg_proc.wait = AsyncMock(return_value=1)
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec',
                 side_effect=[mock_ffmpeg_proc, mock_v4l2_ctl_proc])
    mock_vcr = MagicMock()
    mock_vcr.get_vtr_mode.return_value = MagicMock(vtr_mode=VTRMode.PLAY_FWD)
    result = await _a_main(video_device='video_device',
                           audio_device='audio_device',
                           length=10,
                           output='output',
                           input_index=1,
                           vbi_device=None,
                           vcr=mock_vcr)
    assert result == 1


@pytest.mark.asyncio
async def test_a_main_change_input_proc_error(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.adebug_sleep', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.psutil.pid_exists', return_value=False)
    mocker.patch('vcrtool.capture_stereo.Path.unlink')
    mocker.patch('vcrtool.capture_stereo.Path.stem', return_value='output_base')
    mock_ffmpeg_proc = AsyncMock()
    mock_ffmpeg_proc.pid = 1234
    mock_ffmpeg_proc.wait = AsyncMock(return_value=0)
    mock_change_input_proc = AsyncMock()
    mock_change_input_proc.pid = 5678
    mock_change_input_proc.returncode = 1  # Simulate error
    mock_change_input_proc.wait = AsyncMock(return_value=1)
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec',
                 side_effect=[mock_ffmpeg_proc, mock_change_input_proc])
    mock_vcr = MagicMock()
    mock_vcr.get_vtr_mode.return_value = MagicMock(vtr_mode=VTRMode.PLAY_FWD)
    with pytest.raises(click.Abort):
        await _a_main(video_device='video_device',
                      audio_device='audio_device',
                      length=10,
                      output='output',
                      input_index=1,
                      vbi_device=None,
                      vcr=mock_vcr)
    mock_change_input_proc.wait.assert_called_once()
    mock_vcr.reset_counter.assert_not_called()
    mock_vcr.play.assert_not_called()
    mock_ffmpeg_proc.terminate.assert_not_called()


@pytest.mark.asyncio
async def test_a_main_keyboard_interrupt(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.adebug_sleep', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.psutil.pid_exists', side_effect=[True])
    mocker.patch('vcrtool.capture_stereo.Path.unlink')
    mocker.patch('vcrtool.capture_stereo.Path.stem', return_value='output_base')
    mock_v4l2_ctl_proc = AsyncMock()
    mock_v4l2_ctl_proc.pid = 1234
    mock_v4l2_ctl_proc.returncode = 0
    mock_v4l2_ctl_proc.wait = AsyncMock(return_value=0)
    mock_ffmpeg_proc = AsyncMock()
    mock_ffmpeg_proc.pid = 1234
    mock_ffmpeg_proc.wait = AsyncMock(return_value=0)
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec',
                 side_effect=[mock_ffmpeg_proc, mock_v4l2_ctl_proc])
    mock_vcr = MagicMock()
    mock_vcr.get_vtr_mode.side_effect = KeyboardInterrupt  # Simulate KeyboardInterrupt
    mock_vcr.reset_counter = MagicMock()
    mock_vcr.play = MagicMock()
    result = await _a_main(video_device='video_device',
                           audio_device='audio_device',
                           length=10,
                           output='output',
                           input_index=1,
                           vbi_device=None,
                           vcr=mock_vcr)
    assert result == 0
    mock_vcr.reset_counter.assert_called_once()
    mock_vcr.play.assert_called_once()
    mock_ffmpeg_proc.terminate.assert_called_once()


@pytest.mark.asyncio
async def test_a_main_vbi_proc_terminate_error(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.adebug_sleep', new_callable=AsyncMock)
    mocker.patch('vcrtool.capture_stereo.psutil.pid_exists', side_effect=[True, False])
    mocker.patch('vcrtool.capture_stereo.Path.unlink')
    mocker.patch('vcrtool.capture_stereo.Path.stem', return_value='output_base')
    mock_v4l2_ctl_proc = AsyncMock()
    mock_v4l2_ctl_proc.pid = 1234
    mock_v4l2_ctl_proc.returncode = 0
    mock_v4l2_ctl_proc.wait = AsyncMock(return_value=0)
    mock_ffmpeg_proc = AsyncMock()
    mock_ffmpeg_proc.pid = 1234
    mock_ffmpeg_proc.wait = AsyncMock(return_value=0)
    mock_vbi_proc = AsyncMock()
    mock_vbi_proc.terminate = MagicMock(side_effect=ProcessLookupError)
    mocker.patch('vcrtool.capture_stereo.adebug_create_subprocess_exec',
                 side_effect=[mock_ffmpeg_proc, mock_vbi_proc, mock_v4l2_ctl_proc])
    mock_vcr = MagicMock()
    mock_vcr.get_vtr_mode.return_value = MagicMock(vtr_mode=VTRMode.PLAY_FWD)
    result = await _a_main(video_device='video_device',
                           audio_device='audio_device',
                           length=10,
                           output='output',
                           input_index=1,
                           vbi_device='vbi_device',
                           vcr=mock_vcr)

    assert result == 0
    mock_vbi_proc.terminate.assert_called_once()


@pytest.mark.parametrize(
    ('args', 'expected_exit_code'),
    [
        (['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', 'output'], 0),
        (['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', '-t', 'invalid', 'output'
          ], 1),
        (['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', '-b', 'vbi_device', 'output'
          ], 0),
        (['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', '-i', '3', 'output'], 0),
    ],
)
def test_main_success(mocker: MockerFixture, runner: CliRunner, args: list[str],
                      expected_exit_code: int) -> None:
    mocker.patch('vcrtool.capture_stereo.get_pipewire_audio_device_node_id',
                 return_value=('audio_device_name', 'audio_node_id'))
    mocker.patch('vcrtool.capture_stereo.audio_device_is_available', return_value=True)
    mocker.patch('vcrtool.capture_stereo.sp.run')
    mocker.patch('vcrtool.capture_stereo.debug_sleep')
    mock_vcr = mocker.patch('vcrtool.capture_stereo.JLIP')
    mock_vcr_instance = mock_vcr.return_value
    mock_vcr_instance.get_vtr_mode.return_value = MagicMock(tape_inserted=True)
    mock_vcr_instance.rewind_wait = MagicMock()
    mock_vcr_instance.turn_on = MagicMock()
    mocker.patch('vcrtool.capture_stereo.asyncio.run', return_value=0)

    result = runner.invoke(main, args)

    assert result.exit_code == expected_exit_code
    if expected_exit_code == 0:
        mock_vcr_instance.turn_on.assert_called_once()
        mock_vcr_instance.rewind_wait.assert_called()


def test_main_no_tape_inserted(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch('vcrtool.capture_stereo.get_pipewire_audio_device_node_id',
                 return_value=('audio_device_name', 'audio_node_id'))
    mocker.patch('vcrtool.capture_stereo.audio_device_is_available', return_value=True)
    mocker.patch('vcrtool.capture_stereo.sp.run')
    mocker.patch('vcrtool.capture_stereo.debug_sleep')
    mock_vcr = mocker.patch('vcrtool.capture_stereo.JLIP')
    mock_vcr_instance = mock_vcr.return_value
    mock_vcr_instance.get_vtr_mode.return_value = MagicMock(tape_inserted=False)
    mock_vcr_instance.turn_on = MagicMock()

    result = runner.invoke(main,
                           ['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', 'output'])

    assert result.exit_code == 1
    mock_vcr_instance.turn_on.assert_called_once()


def test_main_audio_device_unavailable(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch('vcrtool.capture_stereo.get_pipewire_audio_device_node_id',
                 return_value=('audio_device_name', 'audio_node_id'))
    mocker.patch('vcrtool.capture_stereo.audio_device_is_available', return_value=False)
    mocker.patch('vcrtool.capture_stereo.sp.run')
    mocker.patch('vcrtool.capture_stereo.debug_sleep')
    result = runner.invoke(main,
                           ['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', 'output'])
    assert result.exit_code == 1


def test_main_audio_node_id_not_found(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch('vcrtool.capture_stereo.get_pipewire_audio_device_node_id',
                 return_value=(None, None))
    mocker.patch('vcrtool.capture_stereo.audio_device_is_available', return_value=True)
    mocker.patch('vcrtool.capture_stereo.sp.run')
    mocker.patch('vcrtool.capture_stereo.debug_sleep')
    result = runner.invoke(main,
                           ['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', 'output'])
    assert result.exit_code == 1
    assert 'Unable to find audio node ID.' in result.output


def test_main_recording_failed(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch('vcrtool.capture_stereo.get_pipewire_audio_device_node_id',
                 return_value=('audio_device_name', 'audio_node_id'))
    mocker.patch('vcrtool.capture_stereo.audio_device_is_available', return_value=True)
    mocker.patch('vcrtool.capture_stereo.sp.run')
    mocker.patch('vcrtool.capture_stereo.debug_sleep')
    mock_vcr = mocker.patch('vcrtool.capture_stereo.JLIP')
    mock_vcr_instance = mock_vcr.return_value
    mock_vcr_instance.get_vtr_mode.return_value = MagicMock(tape_inserted=True)
    mock_vcr_instance.rewind_wait = MagicMock()
    mock_vcr_instance.turn_on = MagicMock()
    mocker.patch('vcrtool.capture_stereo.asyncio.run', return_value=1)  # Simulate recording failure

    result = runner.invoke(main,
                           ['-a', 'audio_device', '-v', 'video_device', '-s', 'serial', 'output'])

    assert result.exit_code == 1
    assert 'Recording failed.' in result.output
    mock_vcr_instance.turn_on.assert_called_once()
    mock_vcr_instance.rewind_wait.assert_called()

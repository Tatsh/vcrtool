from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from vcrtool.utils import (
    adebug_create_subprocess_exec,
    adebug_sleep,
    audio_device_is_available,
    debug_sleep,
    debug_sp_run,
    get_pipewire_audio_device_node_id,
    pad_right,
)
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_pad_right() -> None:
    assert pad_right(0, [1, 2], 5) == [1, 2, 0, 0, 0]
    assert pad_right('x', ['a'], 3) == ['a', 'x', 'x']
    with pytest.raises(ValueError, match='-1'):
        pad_right(0, [1, 2, 3], 2)


def test_debug_sp_run(mocker: MockerFixture) -> None:
    mock_run = mocker.patch('subprocess.run', return_value=MagicMock(stderr=''))
    result = debug_sp_run(['echo', 'hello'])
    mock_run.assert_called_once_with(['echo', 'hello'], check=False)
    assert not result.stderr


def test_audio_device_is_available(mocker: MockerFixture) -> None:
    mock_debug_sp_run = mocker.patch('vcrtool.utils.debug_sp_run',
                                     return_value=MagicMock(stderr=''))
    assert audio_device_is_available('hw:0,0') is True
    mock_debug_sp_run.assert_called_once_with(
        ('ffmpeg', '-hide_banner', '-f', 'alsa', '-i', 'hw:0,0'), capture_output=True, text=True)


def test_audio_device_is_not_available(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.utils.debug_sp_run',
                 return_value=MagicMock(stderr='Device or resource busy'))
    assert audio_device_is_available('hw:0,0') is False


def test_get_pipewire_audio_device_node_id(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.utils.debug_sp_run',
                 side_effect=[
                     MagicMock(stdout='ATTRS{product}=="Test Device"\n'),
                     MagicMock(stdout='Test Device 123\n')
                 ])
    name, node_id = get_pipewire_audio_device_node_id('hw:0,0')
    assert name == 'Test Device'
    assert node_id == '123'


def test_get_pipewire_audio_device_node_id_invalid_device(mocker: MockerFixture) -> None:
    with pytest.raises(ValueError, match='Invalid ALSA device string: invalid_device'):
        get_pipewire_audio_device_node_id('invalid_device')


def test_get_pipewire_audio_device_node_id_not_found(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.utils.debug_sp_run',
                 side_effect=[
                     MagicMock(stdout='ATTRS{product}=="Test Device"\n'),
                     MagicMock(stdout=''),
                 ])
    name, node_id = get_pipewire_audio_device_node_id('hw:0,0')
    assert name is None
    assert node_id is None


def test_get_pipewire_audio_device_node_id_no_match(mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.utils.debug_sp_run',
                 side_effect=[
                     MagicMock(stdout='ATTRS{product}=="Test Device"\n'),
                     MagicMock(stdout='a. Test Device'),
                 ])
    mocker.patch('vcrtool.utils.re.search', return_value=None)
    name, node_id = get_pipewire_audio_device_node_id('hw:0,0')
    assert name is None
    assert node_id is None


@pytest.mark.asyncio
async def test_adebug_sleep(mocker: MockerFixture) -> None:
    mock_sleep = mocker.patch('vcrtool.utils.asyncio.sleep')
    await adebug_sleep(1.5)
    mock_sleep.assert_called_once_with(1.5)


def test_debug_sleep(mocker: MockerFixture) -> None:
    mock_sleep = mocker.patch('vcrtool.utils.sleep')
    debug_sleep(2)
    mock_sleep.assert_called_once_with(2)


@pytest.mark.asyncio
async def test_adebug_create_subprocess_exec(mocker: MockerFixture) -> None:
    mock_create_subprocess_exec = mocker.patch('vcrtool.utils.asp.create_subprocess_exec')
    await adebug_create_subprocess_exec('ls', '-l')
    mock_create_subprocess_exec.assert_called_once_with('ls', '-l')

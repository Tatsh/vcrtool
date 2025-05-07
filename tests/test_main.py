from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
import json

from vcrtool.main import VALID_COMMANDS, jlip
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_jlip_no_command(runner: CliRunner) -> None:
    result = runner.invoke(jlip, ['serial_device'])
    assert result.exit_code != 0
    assert 'No command provided.' in result.output


def test_jlip_invalid_command(runner: CliRunner) -> None:
    result = runner.invoke(jlip, ['serial_device', 'invalid-command'])
    assert result.exit_code != 0
    assert 'Invalid command `invalid-command`.' in result.output
    assert 'Valid commands:' in result.output


@dataclass
class _FakeDataclass:
    success: bool = True


@pytest.mark.parametrize('command', VALID_COMMANDS)
def test_jlip_valid_command(runner: CliRunner, mocker: MockerFixture, command: str) -> None:
    mock_jlip = mocker.patch('vcrtool.main.JLIP')
    mock_instance = mock_jlip.return_value
    mock_method = mocker.Mock(return_value=_FakeDataclass())
    setattr(mock_instance, command.replace('-', '_'), mock_method)
    result = runner.invoke(jlip, ['serial_device', command, '1', '2'])
    assert result.exit_code == 0
    mock_jlip.assert_called_once_with('serial_device', raise_on_error_response=False)
    mock_method.assert_called_once_with(1, 2)
    assert json.loads(result.output) == {'success': True}


def test_jlip_debug_logging(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('vcrtool.main.VALID_COMMANDS', ['valid-command'])
    mock_setup_logging = mocker.patch('vcrtool.main.setup_logging')
    mock_jlip = mocker.patch('vcrtool.main.JLIP')
    mock_instance = mock_jlip.return_value
    mock_method = mocker.Mock(return_value=_FakeDataclass())
    mock_instance.valid_command = mock_method
    result = runner.invoke(jlip, ['serial_device', 'valid-command', '--debug'])
    assert result.exit_code == 0
    mock_setup_logging.assert_called_once_with(debug=True)

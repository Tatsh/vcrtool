from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vcrtool.sircs import SIRCS
import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_gpio(mocker: MockerFixture) -> Any:
    """Fixture to mock the GpioAsyncController."""
    mock_gpio = mocker.patch('vcrtool.sircs.GpioAsyncController', autospec=True)
    return mock_gpio.return_value


@pytest.fixture
def sircs(mock_gpio: MagicMock) -> SIRCS:
    """Fixture to create a SIRCS instance with mocked GPIO."""
    return SIRCS()


def test_logic1(sircs: MagicMock, mock_gpio: MagicMock) -> None:
    """Test the logic1 method."""
    sircs.logic1()
    mock_gpio.write.assert_called_once_with(255)


def test_logic0(sircs: MagicMock, mock_gpio: MagicMock) -> None:
    """Test the logic0 method."""
    sircs.logic0()
    mock_gpio.write.assert_called_once_with(0)


def test_send_command_all_ones(sircs: MagicMock, mocker: MockerFixture) -> None:
    """Test send_command with all bits set to 1."""
    mock_debug_sleep = mocker.patch('vcrtool.sircs.debug_sleep')
    sircs.send_command([1, 1, 1])
    assert mock_debug_sleep.call_count == 7
    mock_debug_sleep.assert_any_call(0.0012)
    mock_debug_sleep.assert_any_call(0.0006)


def test_send_command_all_zeros(sircs: MagicMock, mocker: MockerFixture) -> None:
    """Test send_command with all bits set to 0."""
    mock_debug_sleep = mocker.patch('vcrtool.sircs.debug_sleep')
    sircs.send_command([0, 0, 0])
    assert mock_debug_sleep.call_count == 7
    mock_debug_sleep.assert_any_call(0.0006)


def test_send_command_mixed_bits(sircs: MagicMock, mocker: MockerFixture) -> None:
    """Test send_command with a mix of 1s and 0s."""
    mock_debug_sleep = mocker.patch('vcrtool.sircs.debug_sleep')
    sircs.send_command([1, 0, 1])
    assert mock_debug_sleep.call_count == 7
    mock_debug_sleep.assert_any_call(0.0012)
    mock_debug_sleep.assert_any_call(0.0006)


def test_send_command_timing(sircs: MagicMock, mocker: MockerFixture) -> None:
    """Test send_command ensures total timing is correct."""
    mock_debug_sleep = mocker.patch('vcrtool.sircs.debug_sleep')
    sircs.send_command([1, 1, 1])
    total_sleep_time = sum(call.args[0] for call in mock_debug_sleep.call_args_list)
    assert pytest.approx(total_sleep_time, 0.001) == 0.045

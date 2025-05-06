from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_main(runner: CliRunner, mocker: MockerFixture) -> None:
    assert 1 + 1 == 2

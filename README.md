# vcrtool

[![Python versions](https://img.shields.io/pypi/pyversions/vcrtool.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/vcrtool)](https://pypi.org/project/vcrtool/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/vcrtool)](https://github.com/Tatsh/vcrtool/tags)
[![License](https://img.shields.io/github/license/Tatsh/vcrtool)](https://github.com/Tatsh/vcrtool/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/vcrtool/v0.0.0/master)](https://github.com/Tatsh/vcrtool/compare/v0.0.0...master)
[![QA](https://github.com/Tatsh/vcrtool/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/vcrtool/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/vcrtool/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/vcrtool/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/vcrtool/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/vcrtool?branch=master)
[![Documentation Status](https://readthedocs.org/projects/vcrtool/badge/?version=latest)](https://vcrtool.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3)](http://www.pydocstyle.org/en/stable/)
[![pytest](https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black)](https://docs.pytest.org/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/vcrtool/month)](https://pepy.tech/project/vcrtool)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/vcrtool?logo=github&style=flat)](https://github.com/Tatsh/vcrtool/stargazers)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh)](https://bsky.app/profile/Tatsh.bsky.social)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)

Control a JLIP device such as a VCR.

## Installation

### Poetry

```shell
poetry add vcrtool
```

### Pip

```shell
pip install vcrtool
```

## Usage

```shell
Usage: jlip [OPTIONS] SERIAL_DEVICE [ARGS]...

  Run JLIP commands.

Options:
  -d, --debug  Enable debug logging.
  -h, --help   Show this message and exit.
```

The output is always JSON formatted.

### Valid JLIP Commands

All arguments to the commands are integers. Refer to JLIP documentation for valid values.

Most of these commands are specific to VCRs but many apply to other devices such as DVD players.

- `eject-wait`: Eject the video and block until the video is ejected.
- `eject`: Eject the video.
- `fast-forward`: Fast forward the video.
- `fast-play-backward`: Fast rewind the video and play.
- `fast-play-forward`: Fast forward the video and play.
- `frame-step-back`: Step the video one frame backward.
- `frame-step`: Step the video one frame forward.
- `get-baud-rate-supported`: Get the baud rate supported by the device.
- `get-device-code`: Get the device code.
- `get-device-name`: Get the device name.
- `get-input`: Get the input.
- `get-machine-code`: Get the machine code.
- `get-play-speed`: Get the play speed.
- `get-power-state`: Get the power state.
- `get-tuner-mode`: Get the tuner mode.
- `get-vtr`: Get the VTR.
- `nop`: No operation.
- `pause-recording`: Pause the recording.
- `pause`: Pause the video.
- `play`: Play the video.
- `presence-check`: Check if the device is connected.
- `preset-channel-down`: Navigate one channel down in preset channels.
- `preset-channel-up`: Navigate one channel up in preset channels.
- `real-channel-down`: Navigate one channel down.
- `real-channel-up`: Navigate one channel up.
- `record`: Record to the media.
- `rewind`: Rewind the video.
- `select-band BAND`: Select the band.
- `select-preset-channel CHAN`: Select the preset channel.
- `select-real-channel CHAN`: Select the channel.
- `send-command CMD ARG ...`: Send a custom command to the device.
- `set-channel CHAN`: Set the channel.
- `set-input N NN`: Set the input.
- `set-jlip-id ID`: Set the JLIP ID.
- `set-record-mode MODE`: Set the record mode.
- `set-record-speed SPEED`: Set the record speed.
- `slow-play-backward`: Slow rewind the video.
- `slow-play-forward`: Slow forward the video.
- `stop`: Stop the video.
- `turn-off`: Turn off the device.
- `turn-on`: Turn on the device.

### Example Usage

```shell
# Check if device is connected.
jlip /dev/ttyUSB0 presence-check

# Eject the video but do not block.
jlip /dev/ttyUSB0 eject

# Eject the video and block until the video is ejected.
jlip /dev/ttyUSB0 eject-wait

# Fast forward the video.
jlip /dev/ttyUSB0 fast-forward

# Rewind the video.
jlip /dev/ttyUSB0 rewind

# No operation.
jlip /dev/ttyUSB0 nop
```

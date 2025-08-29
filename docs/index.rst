vcrtool
=======

.. only:: html

   .. image:: https://img.shields.io/pypi/pyversions/vcrtool.svg?color=blue&logo=python&logoColor=white
      :target: https://www.python.org/
      :alt: Python versions

   .. image:: https://img.shields.io/pypi/v/vcrtool
      :target: https://pypi.org/project/vcrtool/
      :alt: PyPI Version

   .. image:: https://img.shields.io/github/v/tag/Tatsh/vcrtool
      :target: https://github.com/Tatsh/vcrtool/tags
      :alt: GitHub tag (with filter)

   .. image:: https://img.shields.io/github/license/Tatsh/vcrtool
      :target: https://github.com/Tatsh/vcrtool/blob/master/LICENSE.txt
      :alt: License

   .. image:: https://img.shields.io/github/commits-since/Tatsh/vcrtool/v0.0.1/master
      :target: https://github.com/Tatsh/vcrtool/compare/v0.0.1...master
      :alt: GitHub commits since latest release (by SemVer including pre-releases)

   .. image:: https://github.com/Tatsh/vcrtool/actions/workflows/codeql.yml/badge.svg
      :target: https://github.com/Tatsh/vcrtool/actions/workflows/codeql.yml
      :alt: CodeQL

   .. image:: https://github.com/Tatsh/vcrtool/actions/workflows/qa.yml/badge.svg
      :target: https://github.com/Tatsh/vcrtool/actions/workflows/qa.yml
      :alt: QA

   .. image:: https://github.com/Tatsh/vcrtool/actions/workflows/tests.yml/badge.svg
      :target: https://github.com/Tatsh/vcrtool/actions/workflows/tests.yml
      :alt: Tests

   .. image:: https://coveralls.io/repos/github/Tatsh/vcrtool/badge.svg?branch=master
      :target: https://coveralls.io/github/Tatsh/vcrtool?branch=master
      :alt: Coverage Status

   .. image:: https://readthedocs.org/projects/vcrtool/badge/?version=latest
      :target: https://vcrtool.readthedocs.org/?badge=latest
      :alt: Documentation Status

   .. image:: https://www.mypy-lang.org/static/mypy_badge.svg
      :target: http://mypy-lang.org/
      :alt: mypy

   .. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
      :target: https://github.com/pre-commit/pre-commit
      :alt: pre-commit

   .. image:: https://img.shields.io/badge/pydocstyle-enabled-AD4CD3
      :target: http://www.pydocstyle.org/en/stable/
      :alt: pydocstyle

   .. image:: https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black
      :target: https://docs.pytest.org/en/stable/
      :alt: pytest

   .. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
      :target: https://github.com/astral-sh/ruff
      :alt: Ruff

   .. image:: https://static.pepy.tech/badge/vcrtool/month
      :target: https://pepy.tech/project/vcrtool
      :alt: Downloads

   .. image:: https://img.shields.io/github/stars/Tatsh/vcrtool?logo=github&style=flat
      :target: https://github.com/Tatsh/vcrtool/stargazers
      :alt: Stargazers

   .. image:: https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh
      :target: https://bsky.app/profile/Tatsh.bsky.social
      :alt: Follow @Tatsh

   .. image:: https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social
      :target: https://hostux.social/@Tatsh
      :alt: Mastodon Follow

Control a JLIP device such as a VCR.

Commands
--------

.. click:: vcrtool.main:jlip
   :prog: jlip
   :nested: full

The output is always JSON formatted.

Valid JLIP commands
^^^^^^^^^^^^^^^^^^^

All arguments to the commands are integers. Refer to JLIP documentation for valid values.

Most of these commands are specific to VCRs but many apply to other devices such as DVD players.

- ``eject-wait``: Eject the video and block until the video is ejected.
- ``eject``: Eject the video.
- ``fast-forward``: Fast forward the video.
- ``fast-play-backward``: Fast rewind the video and play.
- ``fast-play-forward``: Fast forward the video and play.
- ``frame-step-back``: Step the video one frame backward.
- ``frame-step``: Step the video one frame forward.
- ``get-baud-rate-supported``: Get the baud rate supported by the device.
- ``get-device-code``: Get the device code.
- ``get-device-name``: Get the device name.
- ``get-input``: Get the input.
- ``get-machine-code``: Get the machine code.
- ``get-play-speed``: Get the play speed.
- ``get-power-state``: Get the power state.
- ``get-tuner-mode``: Get the tuner mode.
- ``get-vtr``: Get the VTR.
- ``nop``: No operation.
- ``pause-recording``: Pause the recording.
- ``pause``: Pause the video.
- ``play``: Play the video.
- ``presence-check``: Check if the device is connected.
- ``preset-channel-down``: Navigate one channel down in preset channels.
- ``preset-channel-up``: Navigate one channel up in preset channels.
- ``real-channel-down``: Navigate one channel down.
- ``real-channel-up``: Navigate one channel up.
- ``record``: Record to the media.
- ``rewind``: Rewind the video.
- ``select-band BAND``: Select the band.
- ``select-preset-channel CHAN``: Select the preset channel.
- ``select-real-channel CHAN``: Select the channel.
- ``send-command CMD ARG ...``: Send a custom command to the device.
- ``set-channel CHAN``: Set the channel.
- ``set-input N NN``: Set the input.
- ``set-jlip-id ID``: Set the JLIP ID.
- ``set-record-mode MODE``: Set the record mode.
- ``set-record-speed SPEED``: Set the record speed.
- ``slow-play-backward``: Slow rewind the video.
- ``slow-play-forward``: Slow forward the video.
- ``stop``: Stop the video.
- ``turn-off``: Turn off the device.
- ``turn-on``: Turn on the device.

Example usage
^^^^^^^^^^^^^

.. code-block:: shell

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

.. click:: vcrtool.capture_stereo:main
   :prog: capture-stereo
   :nested: full

.. only:: html

   .. toctree::
      :maxdepth: 2
      :caption: Contents:

      lib
      notes

  Indices and tables
  ==================
  * :ref:`genindex`
  * :ref:`modindex`

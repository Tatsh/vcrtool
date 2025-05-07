vcrtool
=======

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

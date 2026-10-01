Other notes
===========

JLIP research
-------------

These commands are not guaranteed to work on anything other than the HR-S9600U and similar model
VCRs. Not responsible if any one of these fries your devices.

Most of the unknown codes were discovered by examining the raw data in the JVC Video Player binary.
The unknown codes below may be for other hardware like video editing equipment.

These commands are tested against HR-S9600U and HR-S9900U. Return values are from or pertain to
those devices.

.. list-table:: JLIP Commands
   :header-rows: 1
   :widths: 20 80

   * - Code
     - Description
   * - ``08 41 60 00 00 00 00``
     - Eject
   * - ``08 42 6D 00 00 00 00``
     - Pause Recording
   * - ``08 42 70 00 00 00 00``
     -
   * - ``08 43 20 00 00 00 00``
     - Slow Play Forward
   * - ``08 43 21 00 00 00 00``
     - Fast Play Forward
   * - ``08 43 24 00 00 00 00``
     - Slow Play Backward
   * - ``08 43 25 00 00 00 00``
     - Fast Play Backward
   * - ``08 43 65 00 00 00 00``
     - Returns not implemented
   * - ``08 43 6D 00 00 00 00``
     - Pause
   * - ``08 43 75 00 00 00 00``
     - Play
   * - ``08 44 60 00 00 00 00``
     - Stop
   * - ``08 44 65 00 00 00 00``
     - Rewind
   * - ``08 44 75 00 00 00 00``
     - FF
   * - ``08 4E 20 00 00 00 00``
     - Get VTR Mode
   * - ``3E 40 60 00 00 00 00``
     - Turn off
   * - ``3E 40 70 00 00 00 00``
     - Turn on
   * - ``3E 4E 20 00 00 00 00``
     - Get Power State
   * - ``48 46 65 01 00 00 00``
     - Single frame advance backward (must be paused first)
   * - ``48 46 75 01 00 00 00``
     - Single frame advance forward
   * - ``48 4E 20 00 00 00 00``
     - Get Play Speed
   * - ``48 50 60 00 00 00 00``
     -
   * - ``48 50 70 00 00 00 00``
     -
   * - ``7C 40 60 00 00 00 00``
     - Unknown return: ``0x03 0x00 ...``
   * - ``7C 40 70 00 00 00 00``
     - Unknown return: ``0x03 0x00 ...``
   * - ``7C 41 FF 00 00 00 00``
     - Set JLIP ID in 3rd field
   * - ``7C 43 60 00 00 00 00``
     - Returns not implemented
   * - ``7C 43 70 00 00 00 00``
     - Returns not implemented
   * - ``7C 44 FF FF FF FF 00``
     - Returns not implemented
   * - ``7C 45 00 00 00 00 00``
     - Get machine code
   * - ``7C 48 20 00 00 00 00``
     - Get baud rate (claims 19200 but it is not true)
   * - ``7C 49 00 00 00 00 00``
     - Get device code
   * - ``7C 4C 00 00 00 00 00``
     - Get device name in ASCII
   * - ``7C 4D 00 00 00 00 00``
     - Get second half of device name in ASCII (returns not implemented)
   * - ``7C 4E 20 00 00 00 00``
     - No operation

HR-S9600EU notes
----------------

The European HR-S9600EU (PAL) works with the same commands. The notes below were collected on that
model.

Connection
^^^^^^^^^^

The J-terminal is a 3.5 mm four-pole jack. According to the service manual (J7108), pin 3 is
ground, pins 4 and 2 carry data to and from the TXD and RXD pins of the sub CPU through 1 kΩ
resistors and clamp diodes, and pin 1 is not connected. The signals use 5 V logic and idle high.

A plain FTDI FT232RL USB-to-TTL adapter set to 5 V works without a level shifter. With a camcorder
AV cable (jack to three RCA plugs), the shields are ground, the white core goes to the RX pin of
the adapter, the yellow core goes to the TX pin (both through 1 kΩ in series), and the red core is
not used.

The serial settings are 9600 baud, 8 data bits, odd parity, 1 stop bit, and no hardware flow
control. The default JLIP ID is 1. A bare USB-to-TTL adapter does not wire CTS, so opening the port
with RTS/CTS flow control enabled may block transmission.

The device replies with the name ``VCR``, machine code ``00 01 00 04 0C 00``, device code
``01 08 48 0A 7F 00``, and baud rate code ``0x21``.

VTR mode response
^^^^^^^^^^^^^^^^^

- When the tape is rewound past 0:00:00, the VCR shows a negative counter such as ``-2:19:15``. The
  minute byte then has bit ``0x40`` set as the minus sign (``0x53`` is 0x40 + 19 minutes).
- The PAL bit reflects the system of the deck, not of the tape. It stays set when an NTSC tape is
  played on this PAL model.
- The counter is driven by the control track and assumes 25 pulses per second. An NTSC tape has
  29.97, so during playback the counter runs about 1.2 times faster than real time (measured 1.21
  to 1.24 for NTSC and 0.99 for PAL). This makes it possible to detect an NTSC tape after a few
  seconds of playback.
- The recordable bit is clear when the write-protect tab of the tape is removed.

Query scan
^^^^^^^^^^

The following queries were tried: ``XX 4E 20`` for ``XX`` from ``00`` to ``7F``,
``{08,0A,0C,3E,48,7C} 4C {00,20-2F}``, and ``{08,48} 4E {21-2F}``. Only the known queries are
accepted, with these observations:

- ``48 4C 20`` returns the same data as ``08 4E 20``.
- ``7C 4C`` ignores the third byte and always returns the device name.
- ``08 58 20`` (get input) returns ``00 10 10 7F 7F 7F``.
- ``0A 4E 20`` returns tuner data, but with the status *not implemented*.
- ``48 4E 20`` returns ``0x75`` during normal playback and ``0x7F`` when stopped.

No response differs between a tape recorded in SP and one recorded in LP, so the recording speed
does not seem to be available over JLIP.

The command table in JVC's *JLIP VideoCapture* 3.11 software is identical to the table above,
including the order of the entries.

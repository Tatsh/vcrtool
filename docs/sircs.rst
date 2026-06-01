SIRCS (Sony infrared remote control)
====================================

`SIRCS <https://www.edcheung.com/automa/sircs.htm>`_ is the signalling protocol Sony uses for its
infrared remote controls and its wired ``CONTROL S`` jacks. :py:mod:`vcrtool` implements it with a
*sans-I/O* design: the protocol logic lives in :py:class:`~vcrtool.sansio.SIRCSCodec`, which does no
input or output, and a separate transport class drives the actual hardware. The codec is therefore
trivially testable, and a new delivery path only needs a new transport.

Protocol summary
----------------

A frame begins with a start (header) mark, followed by the data bits, and is padded with a trailing
space so that every frame occupies a fixed period. Each interval is a multiple of a single unit
``T`` of 600 microseconds. Marks are bursts of a 40 kHz carrier over the air, or a plain baseband
level over a wire.

.. list-table:: SIRCS timing
   :header-rows: 1
   :widths: 30 25 45

   * - Interval
     - Duration
     - Notes
   * - Start mark
     - 2400 µs (``4T``)
     - Begins every frame.
   * - Logical one mark
     - 1200 µs (``2T``)
     -
   * - Logical zero mark
     - 600 µs (``1T``)
     -
   * - Space
     - 600 µs (``1T``)
     - Separates every mark.
   * - Frame period
     - 45000 µs
     - The trailing space is stretched to reach it.

Bits are transmitted least-significant first, ordered command, then address, then the extended
field. Three frame widths exist, selected by :py:class:`~vcrtool.sansio.SIRCSVariant`:

.. list-table:: SIRCS variants
   :header-rows: 1
   :widths: 30 70

   * - Variant
     - Payload
   * - ``TWELVE_BIT``
     - 7-bit command, 5-bit address.
   * - ``FIFTEEN_BIT``
     - 7-bit command, 8-bit address.
   * - ``TWENTY_BIT``
     - 7-bit command, 5-bit address, 8-bit extended field.

Sony receivers expect a command to be repeated at least three times.

Encoding and decoding
---------------------

:py:class:`~vcrtool.sansio.SIRCSCodec` converts a :py:class:`~vcrtool.sansio.SIRCSCommand` to and
from a tuple of :py:class:`~vcrtool.sansio.Pulse` intervals. It performs no I/O, so it is trivially
testable.

.. code-block:: python

   from vcrtool.sansio import SIRCSCodec, SIRCSCommand

   codec = SIRCSCodec()
   pulses = codec.encode(SIRCSCommand(command=0x15, address=1), repeat=3)
   # A pulse is (carrier_on, duration_us). Decoding recovers the command:
   assert codec.decode(pulses) == SIRCSCommand(command=0x15, address=1)

:py:meth:`~vcrtool.sansio.SIRCSCodec.decode` inspects only the marks, infers the variant from the
number of data bits, and stops at the next start mark, so a captured repeated signal decodes
directly.

Transport
---------

Timing is the hard part of SIRCS. Driving a pin from the host with one write per pulse and a
:py:func:`time.sleep` between writes cannot hold the protocol's 600 microsecond resolution, because
USB latency and scheduler jitter are both on the order of a millisecond. The package therefore
delegates the timing to a Raspberry Pi Pico over USB serial.

:py:class:`~vcrtool.sircs.PicoSIRCSTransport` holds a :py:class:`~vcrtool.sansio.SIRCSCodec` and
exposes ``send_command`` and ``transmit``. The PC keeps all protocol knowledge; the Pico is a dumb,
precisely-timed output peripheral whose firmware clocks the pin edges with a PIO state machine. The
transport serialises the pulse train into a compact message:

.. list-table:: Pico wire message
   :header-rows: 1
   :widths: 25 75

   * - Bytes
     - Meaning
   * - ``0xA5``
     - Synchronisation byte.
   * - 2 (big-endian)
     - Pulse count.
   * - 3 per pulse
     - Level byte (final pin state), then a 16-bit big-endian duration in microseconds.

The level is the final pin state, so ``invert`` (used for an active-low ``CONTROL S`` jack) is
resolved on the PC and the firmware simply holds the pin at the given level.

.. code-block:: python

   from vcrtool.sircs import PicoSIRCSTransport
   from vcrtool.sansio import SIRCSCommand

   pico = PicoSIRCSTransport('/dev/ttyACM0')   # invert=True for a direct active-low jack
   pico.send_command(SIRCSCommand(command=0x15, address=1))

Wiring
------

The Sony ``CONTROL S`` jack takes the demodulated baseband envelope, so no 40 kHz carrier is needed
over a wire. The jack idles high and is pulled low for a mark, and its logic level may differ from
the controller's, so drive it through a small open-collector stage rather than directly:

.. code-block:: text

   controller pin ──1kΩ──>|base  NPN  collector|──> CONTROL S tip
                                    emitter ──┐
   controller GND ───────────────────────────┴──> jack sleeve (common ground)

Set ``invert=True`` when wiring directly to the jack (idle high, mark low), or ``invert=False``
through the inverting transistor shown. For infrared instead of a wire, replace the jack with an
infrared LED and its current-limiting resistor and enable the carrier.

.. warning::

   The wired levels and the exact jack pinout vary between devices. Measure the idle voltage on the
   tip and confirm it is the ``CONTROL S`` jack (not ``S-LINK`` or ``CONTROL A1``) before
   connecting anything.

Pico firmware sketch
^^^^^^^^^^^^^^^^^^^^^

The following MicroPython sketch runs on the Pico (save it as ``main.py``). The PIO state machine,
clocked at 1 MHz, makes one instruction tick equal one microsecond, so the timing is exact
regardless of what the interpreter is doing.

.. code-block:: python

   import rp2
   from machine import Pin
   import sys

   PIN = 15        # GPIO pin to the transistor or jack
   SYNC = 0xA5


   # Each FIFO word: bit 0 is the pin level, bits 1..31 are the tick count to hold it.
   @rp2.asm_pio(out_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
   def pulse_train():
       wrap_target()
       pull(block)             # OSR <- 32-bit word (blocks until the PC sends one)
       out(pins, 1)            # drive the pin from the LSB (the level)
       out(x, 31)              # remaining 31 bits are the duration in ticks
       label("hold")
       jmp(x_dec, "hold")      # hold the level for X + 1 ticks
       wrap()


   sm = rp2.StateMachine(0, pulse_train, freq=1_000_000, out_base=Pin(PIN))
   sm.active(1)

   stream = sys.stdin.buffer
   while True:
       if stream.read(1) != bytes([SYNC]):     # resync on the sync byte
           continue
       header = stream.read(2)
       count = (header[0] << 8) | header[1]
       for _ in range(count):
           level, high, low = stream.read(3)
           duration = (high << 8) | low
           sm.put((duration << 1) | (level & 1))   # blocks when the FIFO is full, so it self-paces

The ``pull`` and ``out`` instructions add about three microseconds of overhead per pulse, which is
within the SIRCS tolerance but can be subtracted from ``duration`` if tighter timing is wanted. For
production use a dedicated UART or disable the REPL on the serial interface so stray input cannot
desynchronise the stream; the sync byte makes it self-correcting in any case.

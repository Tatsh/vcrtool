# JLIP commands

These commands are not guaranteed to work on anything other than the HR-S9600U and similar model
VCRs. Not responsible if any one of these fries your devices.

Most of the unknown codes were discovered by examining the raw data in the JVC Video Player binary.
The unknown codes below may be for other hardware like video editing equipment.

These commands are tested against HR-S9600U and HR-S9900U. Return values are from or pertain to
those devices.

| Code                   | Description                                                       |
| ---------------------- | ----------------------------------------------------------------- |
| `08 41 60 00 00 00 00` | Eject                                                             |
| `08 42 6D 00 00 00 00` | Pause Recording                                                   |
| `08 42 70 00 00 00 00` |                                                                   |
| `08 43 20 00 00 00 00` | Slow Play Forward                                                 |
| `08 43 21 00 00 00 00` | Fast Play Forward                                                 |
| `08 43 24 00 00 00 00` | Slow Play Backward                                                |
| `08 43 25 00 00 00 00` | Fast Play Backward                                                |
| `08 43 65 00 00 00 00` | Returns not implemented                                           |
| `08 43 6D 00 00 00 00` | Pause                                                             |
| `08 43 75 00 00 00 00` | Play                                                              |
| `08 44 60 00 00 00 00` | Stop                                                              |
| `08 44 65 00 00 00 00` | Rewind                                                            |
| `08 44 75 00 00 00 00` | FF                                                                |
| `08 4E 20 00 00 00 00` | Get VTR Mode                                                      |
| `3E 40 60 00 00 00 00` | Turn off                                                          |
| `3E 40 70 00 00 00 00` | Turn on                                                           |
| `3E 4E 20 00 00 00 00` | Get Power State                                                   |
| `48 46 65 01 00 00 00` | Single frame advance backward (must be paused first)              |
| `48 46 75 01 00 00 00` | Single frame advance forward                                      |
| `48 4E 20 00 00 00 00` | Get Play Speed                                                    |
| `48 50 60 00 00 00 00` |                                                                   |
| `48 50 70 00 00 00 00` |                                                                   |
| `7C 40 60 00 00 00 00` | Unknown return: `0x03 0x00 ...`                                   |
| `7C 40 70 00 00 00 00` | Unknown return: `0x03 0x00 ...`                                   |
| `7C 41 FF 00 00 00 00` | Set JLIP ID in 3rd field                                          |
| `7C 43 60 00 00 00 00` | Returns not implemented                                           |
| `7C 43 70 00 00 00 00` | Returns not implemented                                           |
| `7C 44 FF FF FF FF 00` | Returns not implemented                                           |
| `7C 45 00 00 00 00 00` | Get machine code                                                  |
| `7C 48 20 00 00 00 00` | Get baud rate (claims 19200 but it is not true)                   |
| `7C 49 00 00 00 00 00` | Get device code                                                   |
| `7C 4C 00 00 00 00 00` | Get device name in ASCII                                          |
| `7C 4D 00 00 00 00 00` | Get second half of device name in ASCII (returns not implemented) |
| `7C 4E 20 00 00 00 00` | No operation                                                      |

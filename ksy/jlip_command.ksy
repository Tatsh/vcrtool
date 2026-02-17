# JLIP output command (host → device)

# Ref: vcrtool/vcrtool/jlip.py send_command_base, checksum()

# Fixed 11-byte packet

meta:
  id: jlip_command
  endian: be
  title: JLIP command (output)
  description: |
    JLIP (Joint Level Interface Protocol) command packet sent from host to device.
    Used by JVC VCRs and similar devices (e.g. HR-S9600U).
  license: MIT
seq:
  - id: sync
    type: u2
    valid:
      eq: 0xFFFF
    doc: Sync bytes, must be 0xFF 0xFF
  - id: jlip_id
    type: u1
    doc: JLIP device ID (1-99)
  - id: args
    type: u1
    repeat: expr
    repeat-expr: 7
    doc: Command bytes (padded to 7 with zeros). First bytes are command group, subcommand, etc.
  - id: checksum
    type: u1
    doc: |
      Checksum: (0x80 - sum(sync_hi, sync_lo, jlip_id, args[0..6] & 0x7F)) & 0x7F.
      Only lower 7 bits of each byte are used in the sum.

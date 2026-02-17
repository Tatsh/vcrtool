# JLIP input/response (device → host)

# Ref: vcrtool/vcrtool/jlip.py CommandResponse.from_bytes, CommandStatus

# Fixed 11-byte packet

meta:
  id: jlip_response
  endian: be
  title: JLIP response (input)
  description: |
    JLIP (Joint Level Interface Protocol) response packet from device to host.
    Sent in reply to a command.
  license: MIT
seq:
  - id: sync
    type: u2
    valid:
      eq: 0xFFFF
    doc: Sync bytes, must be 0xFF 0xFF
  - id: jlip_id
    type: u1
    doc: JLIP device ID
  - id: status_byte
    type: u1
    doc: |
      Byte 3. Lower 3 bits are command status (CommandStatus).
      status_byte & 0x07: 1=not implemented, 3=accepted, 4=accepted not complete, 5=not possible
  - id: return_data
    type: u1
    repeat: expr
    repeat-expr: 6
    doc: Return data bytes (payload); interpretation depends on the command
  - id: checksum
    type: u1
    doc: |
      Checksum: (0x80 - sum(sync_hi, sync_lo, jlip_id, status_byte, return_data[0..5] & 0x7F)) & 0x7F.
enums:
  command_status:
    1: command_not_implemented
    3: command_accepted
    4: command_accepted_not_complete
    5: command_not_possible
instances:
  status:
    value: status_byte & 7
    enum: command_status
    doc: Command status from lower 3 bits of status_byte

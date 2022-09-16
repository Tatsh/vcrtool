from pathlib import Path

import click

from vcrtool import CommandStatus, JLIPHRSeriesVCR


@click.command()
@click.argument('devpath')
def main(devpath: str) -> None:
    for i in range(1, 100):
        try:
            if ((JLIPHRSeriesVCR(
                    devpath, jlip_id=i,
                    raise_on_error_response=False).send_command_fast(
                        0x7c, 0x4e, 0x20)[3]
                 & 0b111) == CommandStatus.COMMAND_ACCEPTED):
                if not Path(f'/dev/jlip{i}').exists():
                    click.echo(i)
                    break
        except IndexError:
            continue

import sys
import argparse

from ..util import normalize_str, layout_exists
from ._util import open_config


def convert_command(args: argparse.Namespace) -> None:
    """Convert config files between formats"""

    layout = normalize_str(args.layout)

    if not layout_exists(layout):
        print(f"Layout not found: {args.layout}")
        sys.exit(1)

    fh, des = open_config(args.input, args.input_format, "r")
    with fh:
        config = des.read(fh, layout)

    fh, ser = open_config(args.output, args.output_format, "w")
    with fh:
        ser.write(config, fh, args.layout)

    print(f"Wrote config to {args.output}")

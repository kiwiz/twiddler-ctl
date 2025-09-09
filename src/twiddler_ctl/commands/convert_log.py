import io
import sys
import argparse
from pathlib import Path

from ..util import normalize_str, layout_exists
from ..log import Serdes
from ..log.binary import Binary
from ..log.text import Text


FORMAT_MAP: dict[str, tuple[bool, type[Serdes]]] = {
    "text": (False, Text),
    "binary": (True, Binary),
}


def detect_log_format(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".log":
        return "binary"
    return "text"


def open_log(path: Path, fmt: str | None, mode: str) -> tuple[Serdes, io.FileIO]:
    binary, cls = FORMAT_MAP[fmt or detect_log_format(path)]

    if binary:
        mode += "b"

    return cls, open(path, mode)


def convert_log_command(args: argparse.Namespace) -> None:
    """Convert untethered recordings between formats"""

    layout = normalize_str(args.layout)

    if not layout_exists(layout):
        print(f"Layout not found: {layout}")
        sys.exit(1)

    des, fh = open_log(args.input, args.input_format, "r")
    with fh:
        text = des.read(fh, layout)

    ser, fh = open_log(args.output, args.output_format, "w")
    with fh:
        ser.write(text, fh, layout)

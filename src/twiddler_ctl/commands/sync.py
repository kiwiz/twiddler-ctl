import os
import sys
import argparse
import configparser
import io
from pathlib import Path

from ..config.config7 import Config7
from ..util import normalize_str, layout_exists
from ._util import detect_format, open_config


def sync_command(args: argparse.Namespace) -> None:
    """Sync config files with a Twiddler"""

    parser = configparser.ConfigParser()
    with open(args.config, "r") as fh:
        parser.read_file(fh)

    if "twiddler" not in parser:
        print("[twiddler] is not defined")
        sys.exit(1)

    path = parser["twiddler"].get("path")
    layout = normalize_str(parser["twiddler"].get("layout", fallback="default"))

    if not layout_exists(layout):
        print(f"Layout not found: {layout}")
        sys.exit(1)

    if "configs" not in parser:
        print("[configs] is not defined")
        sys.exit(1)

    for i in [1, 2, 3]:
        fn = parser["configs"].get(str(i))
        target_path = os.path.join(path, f"{i}.cfg")

        curr = None
        if os.path.exists(target_path):
            with open(target_path, "rb") as fh:
                curr = fh.read()

        input_format = detect_format(Path(fn))
        if input_format == "binary":
            with open(fn, "rb") as fh:
                new = fh.read()
        else:
            fh, des = open_config(fn, None, "r")
            with fh:
                config = des.read(fh, layout)
            buf = io.BytesIO()
            Config7.write(config, buf, layout)
            new = buf.getvalue()

        if new == curr:
            continue

        print(f"Updating {i}.cfg with {fn}")
        with open(target_path, "wb") as fh:
            fh.write(new)

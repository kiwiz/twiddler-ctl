#!/usr/bin/env python3
"""
twiddler-ctl
"""

import sys
import argparse
from pathlib import Path

from .commands.convert import convert_command
from .commands._util import FORMAT_MAP
from .commands.visualize import visualize_command
from .commands.sync import sync_command
from .commands.dump import dump_command, KEY_TABLES
from .commands.convert_log import convert_log_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Twiddler configs")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    convert_parser = subparsers.add_parser(
        "convert", help="Convert configs from/to text"
    )
    convert_parser.set_defaults(func=convert_command)
    convert_parser.add_argument("input", type=Path, help="Input file")
    convert_parser.add_argument("output", type=Path, help="Output file")
    convert_parser.add_argument(
        "--layout", type=str, default="default", help="Keyboard layout"
    )
    convert_parser.add_argument(
        "--input-format", choices=FORMAT_MAP.keys(), help="Input format"
    )
    convert_parser.add_argument(
        "--output-format", choices=FORMAT_MAP.keys(), help="Output format"
    )

    visualize_parser = subparsers.add_parser(
        "visualize", help="(WIP) Visualize config layout"
    )
    visualize_parser.set_defaults(func=visualize_command)
    visualize_parser.add_argument("input", type=Path, help="Input file")
    visualize_parser.add_argument(
        "--input-format", choices=FORMAT_MAP.keys(), help="Input format"
    )

    sync_parser = subparsers.add_parser("sync", help="Sync configs")
    sync_parser.set_defaults(func=sync_command)
    sync_parser.add_argument(
        "--config", type=Path, default="config.ini", help="Config file"
    )

    dump_parser = subparsers.add_parser("dump", help="Output valid actions")
    dump_parser.set_defaults(func=dump_command)
    dump_parser.add_argument(
        "--table", default="keys", choices=KEY_TABLES.keys(), help="Target table"
    )

    convert_log_parser = subparsers.add_parser(
        "convert-log", help="Convert untethered recordings from/to text"
    )
    convert_log_parser.set_defaults(func=convert_log_command)
    convert_log_parser.add_argument("input", type=Path, help="Input file")
    convert_log_parser.add_argument("output", type=Path, help="Output file")
    convert_log_parser.add_argument(
        "--layout", type=str, default="default", help="Keyboard layout"
    )
    convert_log_parser.add_argument(
        "--input-format", choices=FORMAT_MAP.keys(), help="Input format"
    )
    convert_log_parser.add_argument(
        "--output-format", choices=FORMAT_MAP.keys(), help="Output format"
    )

    args = parser.parse_args()
    if "func" not in args:
        parser.print_usage()
        sys.exit(0)

    try:
        args.func(args)
    except Exception as e:
        raise e
        print(f"Unhandled error: {args.func}, {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

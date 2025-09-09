import argparse
import itertools

from ..config.text import SYSTEM_COMMANDS, MOUSE_COMMANDS, DEDICATED_KEYS, KEY_MACROS
from ..util import get_forward_mapping

KEY_TABLES = {
    "keys": lambda: itertools.chain(
        get_forward_mapping("default").values(), KEY_MACROS.keys()
    ),
    "application-keys": lambda: get_forward_mapping("default", True).values(),
    "system": lambda: SYSTEM_COMMANDS.keys(),
    "mouse": lambda: MOUSE_COMMANDS.keys(),
    "dedicated-keys": lambda: DEDICATED_KEYS.keys(),
}


def dump_command(args: argparse.Namespace) -> None:
    """Print valid values for the target table"""

    for value in KEY_TABLES[args.table]():
        print(value)

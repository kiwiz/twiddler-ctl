import argparse
import shutil

from ..config.config7 import Config7
from ._util import open_config


KEY_BRAILLE_MAP = [
    (0, 0x40),  # t1
    (1, 0x40),
    (1, 0x80),
    (2, 0x40),
    (3, 0x01),  # t2
    (4, 0x01),
    (4, 0x08),
    (5, 0x01),
    (3, 0x02),  # t3
    (4, 0x02),
    (4, 0x10),
    (5, 0x02),
    (3, 0x04),  # t4
    (4, 0x04),
    (4, 0x20),
    (5, 0x04),
    (1, 0x02),
    (1, 0x10),
    (2, 0x02),
    (0, 0x02),  # t0
]


def _generate_chart(offsets: list[str]) -> tuple[str, str]:
    chart = [0x2800] * 6

    for key in offsets:
        idx, val = KEY_BRAILLE_MAP[key]
        chart[idx] |= val

    return (
        "".join(map(chr, chart[:3])),
        "".join(map(chr, chart[3:])),
    )


def visualize_command(args: argparse.Namespace) -> None:
    fh, des = open_config(args.input, None, "r")
    with fh:
        config = des.read(fh, "default")

    charts = []

    for i, key in enumerate(config.dedicated):
        if key == 0:
            continue

        charts.append(_generate_chart([i]))

    for mapping in config.mappings:
        val = Config7._chord_to_int(mapping.chord)

        offsets = []
        offset = 0
        while val:
            if val & 1:
                offsets.append(offset)
            val = val >> 1
            offset += 1

        charts.append(_generate_chart(offsets))

    cols = shutil.get_terminal_size().columns
    max_per_row = cols // 4

    col_a = []
    col_b = []
    for a, b in charts:
        if len(col_a) >= max_per_row:
            print("|".join(col_a))
            print("|".join(col_b))
            col_a = []
            col_b = []

        col_a.append(a)
        col_b.append(b)

    if col_a:
        print("|".join(col_a))
        print("|".join(col_b))

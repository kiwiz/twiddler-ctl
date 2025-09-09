import io
import struct

from typing import Any

from ..util import get_forward_mapping, get_backward_mapping
from . import Serdes

NAME_MAP = {
    "space": " ",
    "period": ".",
    "comma": ",",
    "tilde": "~",
    "exclamation": "!",
    "at": "@",
    "hash": "#",
    "dollar": "$",
    "percent": "%",
    "caret": "^",
    "ampersand": "&",
    "asterisk": "*",
    "left_parenthesis": "(",
    "right_parenthesis": ")",
    "left_curly_bracket": "{",
    "right_curly_bracket": "}",
    "question": "?",
    "plus": "+",
    "pipe": "|",
    "underscore": "_",
    "colon": ":",
    "double_quote": '"',
    "less_than": "<",
    "greater_than": ">",
}
CHAR_MAP = {v:k for k, v in NAME_MAP.items()}

class Binary(Serdes):
    @staticmethod
    def write(text: str, fh: Any, layout: str) -> None:
        mapping = get_backward_mapping(layout)

        for c in text:
            val = mapping.get(CHAR_MAP.get(c, c))
            fh.write(struct.pack("<I", val))


    @staticmethod
    def read(fh: Any, layout: str) -> str:
        buf = io.StringIO()

        mapping = get_forward_mapping(layout)

        while True:
            raw = fh.read(4)
            if not raw:
                break

            char = mapping.get(struct.unpack("<I", raw)[0], "_")
            buf.write(NAME_MAP.get(char, char))

        return buf.getvalue()

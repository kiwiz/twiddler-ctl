import io
from pathlib import Path

from ..config import Serdes
from ..config.text import Text
from ..config.config7 import Config7

FORMAT_MAP: dict[str, tuple[bool, type[Serdes]]] = {
    "text": (False, Text),
    "binary": (True, Config7),
}


def detect_format(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".cfg":
        return "binary"
    return "text"


def open_config(path: Path, fmt: str | None, mode: str) -> tuple[io.FileIO, Serdes]:
    binary, cls = FORMAT_MAP[fmt or detect_format(path)]

    if binary:
        mode += "b"

    return open(path, mode), cls

from typing import Any

from . import Serdes


class Text(Serdes):
    @staticmethod
    def write(text: str, fh: Any, layout: str) -> None:
        fh.write(text)

    @staticmethod
    def read(fh: Any, layout: str) -> str:
        return fh.read()

from typing import Any


class Serdes:
    @staticmethod
    def write(text: str, f: Any, layout: str) -> None:
        raise NotImplementedError()

    @staticmethod
    def read(fh: Any, layout: str) -> str:
        raise NotImplementedError()

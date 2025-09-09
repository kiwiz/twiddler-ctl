from typing import Any

from ..models import Config


class Serdes:
    @staticmethod
    def write(config: Config, f: Any, layout: str) -> None:
        raise NotImplementedError()

    @staticmethod
    def read(f: Any, layout: str) -> Config:
        raise NotImplementedError()

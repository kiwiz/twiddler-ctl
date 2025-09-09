from dataclasses import dataclass, field
from enum import IntEnum

Row = tuple[bool, bool, bool]


class CommandType(IntEnum):
    NONE = 0
    SYSTEM = 1
    KEYBOARD = 2
    MOUSE = 3
    APPLICATION = 4
    DELAY = 5
    HAPTIC = 6
    COMMAND_LIST = 7


@dataclass
class Chord:
    thumbs: tuple[bool, bool, bool, bool, bool] = field(
        default_factory=lambda: (False, False, False, False, False)
    )
    fingers: tuple[Row, Row, Row, Row, Row] = field(
        default_factory=lambda: (
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
        )
    )


@dataclass
class Command:
    command_type: CommandType
    a: int
    b: int


@dataclass
class Mapping:
    chord: Chord
    commands: list[Command] = field(default_factory=lambda: [])


@dataclass
class Config:
    version: int = 7

    repeat: bool = True
    bluetooth: bool = True
    direct: bool = False
    haptic: bool = True
    sticky_num: bool = False
    sticky_alt: bool = False
    sticky_ctrl: bool = False
    sticky_shift: bool = False
    nav_up_direction: int = 0
    nav_invert_x: bool = False
    nav_sensitivity: int = 0

    idle_time: int = 600
    repeat_delay: int = 100

    dedicated: list[int] = field(default_factory=lambda: [0] * 20)
    mappings: list[Mapping] = field(default_factory=lambda: [])

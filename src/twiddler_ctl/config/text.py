from typing import TextIO
import configparser


from . import Serdes
from ..util import normalize_str, get_backward_mapping, get_forward_mapping
from ..models import Config, Chord, Command, CommandType, Mapping


KEY_MACROS = {
    "tilde": "rshift+backtick",
    "exclamation": "rshift+1",
    "at": "rshift+2",
    "hash": "rshift+3",
    "dollar": "rshift+4",
    "percent": "rshift+5",
    "caret": "rshift+6",
    "ampersand": "rshift+7",
    "asterisk": "rshift+8",
    "left_parenthesis": "rshift+9",
    "right_parenthesis": "rshift+0",
    "left_curly_bracket": "rshift+left_bracket",
    "right_curly_bracket": "rshift+right_bracket",
    "question": "rshift+backslash",
    "plus": "rshift+equal",
    "pipe": "rshift+slash",
    "underscore": "rshift+minus",
    "colon": "rshift+semicolon",
    "double_quote": "rshift+quote",
    "less_than": "rshift+comma",
    "greater_than": "rshift+period",
}
for i in range(0x61, 0x7B):
    KEY_MACROS[chr(i - 0x20)] = f"rshift+{chr(i)}"
MACRO_CODES: dict[str, str] = {v: k for k, v in KEY_MACROS.items()}

DEDICATED_ORDER: list[str] = [
    "t1",
    "f1r",
    "f1m",
    "f1l",
    "t2",
    "f2r",
    "f2m",
    "f2l",
    "t3",
    "f3r",
    "f3m",
    "f3l",
    "t4",
    "f4r",
    "f4m",
    "f4l",
    "f0r",
    "f0m",
    "f0l",
    "t0",
]
DEDICATED_OFFSETS: dict[str, int] = {v: k for k, v in enumerate(DEDICATED_ORDER)}

DEDICATED_KEYS = {
    "lctrl": 0x01,
    "lshift": 0x02,
    "lalt": 0x03,
    "lmeta": 0x04,
    "rctrl": 0x05,
    "rshift": 0x06,
    "ralt": 0x07,
    "rmeta": 0x08,
    "mouse_left": 0x09,
    "mouse_right": 0x0A,
    "mouse_middle": 0x0B,
    "sticky": 0x0C,
    "hyper": 0x0D,
}
DEDICATED_CODES: dict[int, str] = {v: k for k, v in DEDICATED_KEYS.items()}

NAV_DIRECTIONS: dict[str, int] = {
    "north": 0,
    "east": 1,
    "south": 2,
    "west": 3,
}
NAV_CODES: dict[int, str] = {v: k for k, v in NAV_DIRECTIONS.items()}

MODIFIER_KEYS: dict[str, int] = {
    "lctrl": 0x01,
    "lshift": 0x02,
    "lalt": 0x04,
    "lmeta": 0x08,
    "rctrl": 0x10,
    "rshift": 0x20,
    "ralt": 0x40,
    "rmeta": 0x80,
}
MODIFIER_CODES: dict[int, str] = {v: k for k, v in MODIFIER_KEYS.items()}

SYSTEM_COMMANDS: dict[str, int] = {
    "sleep": 0x01,
    "print_system_info": 0x02,
    "toggle_test_mode": 0x03,
    "show_cycle_config": 0x04,
    "show_cycle_bluetooth_host": 0x05,
    "clear_bluetooth_hosts": 0x06,
    "toggle_untethered_mode": 0x07,
    "clear_untethered_mode": 0x08,
    "play_untethered_mode": 0x09,
    "show_battery_level": 0x0A,
    "show_cycle_nav_mode": 0x0B,
    "show_keyboard_leds": 0x0C,
    "print_system_stats": 0x0D,
    "cycle_config": 0x0E,
    "cycle_bluetooth_host": 0x0F,
    "cycle_nav_mode": 0x10,
    "select_config_0": 0x11,
    "select_bluetooth_host": 0x12,
    "select_nav_mode": 0x13,
    "select_config_1": 0x111,
    "select_config_2": 0x211,
    "select_config_3": 0x311,
}
SYSTEM_CODES: dict[int, str] = {v: k for k, v in SYSTEM_COMMANDS.items()}

MOUSE_COMMANDS: dict[str, int] = {
    "release": 0x00,
    "right": 0x01,
    "left": 0x02,
    "middle": 0x04,
}
MOUSE_CODES: dict[int, str] = {v: k for k, v in MOUSE_COMMANDS.items()}


def _keycode_from_text(cmd_txt: str, layout: str) -> int:
    mapping = get_backward_mapping(layout)

    mod = 0
    parts = cmd_txt.split("+")
    key = parts.pop()
    for part in parts:
        mod |= MODIFIER_KEYS.get(normalize_str(part), 0)

    code = mapping.get(normalize_str(key))
    if code is None:
        return None

    return (code << 8) | mod


def _keycode_to_text(val: int, layout: str) -> str:
    mod = val & 0xFF
    key = val >> 8
    mapping = get_forward_mapping(layout)

    parts = []
    for b, name in MODIFIER_CODES.items():
        if b & mod:
            parts.append(name)

    parts.append(mapping[key])
    text = "+".join(parts)

    if text in MACRO_CODES:
        text = MACRO_CODES[text]

    return text


class Text(Serdes):
    COL_CODES = ["R", "M", "L"]
    COL_OFFSETS = {v: k for k, v in enumerate(COL_CODES)}

    @classmethod
    def set_row(cls, fingers, thumbs, row: str, cols: str) -> None:
        idx = int(row)
        for col in cols:
            idxx = cls.COL_OFFSETS.get(col)

            if idx is None:
                continue

            fingers[idx][idxx] = True

    @staticmethod
    def _chord_from_text(notation: str) -> Chord:
        s = notation.strip().upper()
        i = 0
        n = len(s)
        seen_first_finger = False
        thumbs = [False, False, False, False, False]
        fingers = [[False, False, False] for _ in range(5)]

        while i < n:
            ch = s[i]
            # Thumb block: T followed by digits 0..4
            if ch == "T":
                i += 1
                while i < n and s[i] in "01234":
                    thumbs[int(s[i])] = True
                    i += 1
                continue

            # First finger section must start with 'F'
            if ch == "F" and not seen_first_finger:
                i += 1
                if i < n and s[i] in "01234":
                    row = s[i]
                    i += 1
                    start = i
                    while i < n and s[i] in "LMR":
                        i += 1
                    cols = s[start:i]
                    Text.set_row(fingers, thumbs, row, cols)
                    seen_first_finger = True
                continue

            # Subsequent finger sections: digit then L/M/R+
            if seen_first_finger and ch in "01234":
                row = ch
                i += 1
                start = i
                while i < n and s[i] in "LMR":
                    i += 1
                cols = s[start:i]
                Text.set_row(fingers, thumbs, row, cols)
                continue

            # Unknown token; skip one char
            i += 1

        # Convert fingers to tuple of tuples
        fingers_tuple = tuple(tuple(row) for row in fingers)
        thumbs_tuple = tuple(thumbs)
        return Chord(thumbs=thumbs_tuple, fingers=fingers_tuple)

    @staticmethod
    def _chord_to_text(c: Chord) -> str:
        parts: list[str] = []

        thumb = "".join([d for d, on in zip("01234", c.thumbs) if on])
        if thumb:
            parts.append(f"T{thumb}")

        def row_str(row: int, row_vals: tuple[bool, bool, bool]) -> str:
            s: str = ""
            if row_vals[2]:
                s += "L"
            if row_vals[1]:
                s += "M"
            if row_vals[0]:
                s += "R"
            return s

        rows: list[str] = [row_str(i, c.fingers[i]) for i in range(5)]
        first_finger_added = False
        for i, s in enumerate(rows):
            if s:
                if not first_finger_added:
                    parts.append(f"F{i}{s}")
                    first_finger_added = True
                else:
                    parts.append(f"{i}{s}")
        return "".join(parts) if parts else "_"

    @staticmethod
    def _command_from_text(val: str, layout: str) -> Command:
        typ_, *rest = val.split(":", 1)
        if rest:
            val = rest[0]
        else:
            typ_, val = "keyboard", typ_

        if typ_ in set(["system", "sys"]):
            name = normalize_str(val)
            if name not in SYSTEM_COMMANDS:
                raise ValueError(f"Unknown system command: {name}")

            command = Command(CommandType.SYSTEM, SYSTEM_COMMANDS[name], 0)
        elif typ_ in set(["keyboard", "kb"]):
            if val in KEY_MACROS:
                val = KEY_MACROS[val]

            code = _keycode_from_text(val, layout)
            if code is None:
                raise ValueError(f"Invalid key: {val}")
            command = Command(CommandType.KEYBOARD, code, 0)
        elif typ_ in set(["mouse", "ms"]):
            name = normalize_str(val)
            if name not in MOUSE_COMMANDS:
                raise ValueError(f"Unknown mouse command: {name}")

            command = Command(CommandType.MOUSE, MOUSE_COMMANDS[name], 0)
        elif typ_ in set(["application", "con"]):
            name = normalize_str(val)
            code = get_backward_mapping("default", True).get(name)
            command = Command(CommandType.APPLICATION, code, 0)
        elif typ_ in set(["delay", "dly"]):
            command = Command(CommandType.DELAY, int(val) // 10, 0)
        elif typ_ in set(["haptic", "hap"]):
            command = Command(CommandType.HAPTIC, int(val, 16), 0)
        else:
            raise ValueError(f"Unknown command type: {typ_}")

        return command

    @staticmethod
    def read(fh: TextIO, layout: str) -> Config:
        parser = configparser.ConfigParser()
        parser.read_file(fh)
        cfg = Config()

        if "config" in parser:
            section = parser["config"]

            cfg.repeat = section.getboolean("repeat", fallback=cfg.repeat)
            cfg.bluetooth = section.getboolean("bluetooth", fallback=cfg.bluetooth)
            cfg.direct = section.getboolean("direct", fallback=cfg.direct)
            cfg.haptic = section.getboolean("haptic", fallback=cfg.haptic)
            cfg.sticky_num = section.getboolean("sticky_num", fallback=cfg.sticky_num)
            cfg.sticky_alt = section.getboolean("sticky_alt", fallback=cfg.sticky_alt)
            cfg.sticky_ctrl = section.getboolean(
                "sticky_ctrl", fallback=cfg.sticky_ctrl
            )
            cfg.sticky_shift = section.getboolean(
                "sticky_shift", fallback=cfg.sticky_shift
            )
            cfg.nav_up_direction = NAV_CODES.get(
                section.get("nav_up_direction"), cfg.nav_up_direction
            )
            cfg.nav_invert_x = section.getboolean(
                "nav_invert_x", fallback=cfg.nav_invert_x
            )
            cfg.nav_sensitivity = section.getint(
                "nav_sensitivity", fallback=cfg.nav_sensitivity
            )

            cfg.idle_time = section.getint("idle_time", fallback=cfg.idle_time)
            cfg.repeat_delay = (
                section.getint("repeat_delay", fallback=cfg.repeat_delay * 10) // 10
            )

        if "dedicated" in parser:
            for key, val in parser["dedicated"].items():
                key = normalize_str(key)
                if key not in DEDICATED_ORDER:
                    raise ValueError(f"Unknown key: {key}")

                val = normalize_str(val)
                if val not in DEDICATED_KEYS:
                    raise ValueError(f"Unknown action: {val}")

                cfg.dedicated[DEDICATED_OFFSETS[key]] = DEDICATED_KEYS[val]

        if "mappings" in parser:
            cfg.mappings = []

            for key, val in parser["mappings"].items():
                chord = Text._chord_from_text(key)

                cmds = []
                for cmd_txt in val.split():
                    cmds.append(Text._command_from_text(cmd_txt, layout))

                cfg.mappings.append(Mapping(chord, cmds))

        return cfg

    @staticmethod
    def _command_to_text(command: Command, layout: str) -> str:
        assert command.b == 0

        if command.command_type == CommandType.SYSTEM:
            cmd_txt = f"system:{SYSTEM_CODES[command.a]}"
        elif command.command_type == CommandType.KEYBOARD:
            cmd_txt = _keycode_to_text(command.a, layout)
        elif command.command_type == CommandType.MOUSE:
            cmd_txt = f"mouse:{MOUSE_CODES[command.a]}"
        elif command.command_type == CommandType.APPLICATION:
            name = get_forward_mapping("default", True).get(command.a)
            cmd_txt = f"application:{name}"
        elif command.command_type == CommandType.DELAY:
            cmd_txt = f"delay:{command.a * 10}"
        elif command.command_type == CommandType.HAPTIC:
            cmd_txt = f"haptic:{command.a:02x}"  # FIXME: NOT IMPLEMENTED
        else:
            raise ValueError(f"Unknown command type: {command.command_type}")

        return cmd_txt

    @staticmethod
    def write(cfg: Config, f: TextIO, layout: str) -> None:
        lines: list[str] = []
        lines.append("[config]")
        lines.append(f"repeat = {cfg.repeat}")
        lines.append(f"bluetooth = {cfg.bluetooth}")
        lines.append(f"direct = {cfg.direct}")
        lines.append(f"haptic = {cfg.haptic}")
        lines.append(f"sticky_num = {cfg.sticky_num}")
        lines.append(f"sticky_alt = {cfg.sticky_alt}")
        lines.append(f"sticky_ctrl = {cfg.sticky_ctrl}")
        lines.append(f"sticky_shift = {cfg.sticky_shift}")
        lines.append(f"nav_up_direction = {NAV_CODES[cfg.nav_up_direction]}")
        lines.append(f"nav_invert_x = {cfg.nav_invert_x}")
        lines.append(f"nav_sensitivity = {cfg.nav_sensitivity}")
        lines.append(f"idle_time = {cfg.idle_time}")
        lines.append(f"repeat_delay = {cfg.repeat_delay * 10}")

        lines.append("")
        lines.append("[dedicated]")
        for off, val in enumerate(cfg.dedicated):
            # Skip if not set
            if val == 0:
                continue

            lines.append(f"{DEDICATED_ORDER[off].upper()} = {DEDICATED_CODES[val]}")

        lines.append("")
        lines.append("[mappings]")

        for mapping in cfg.mappings:
            notation = Text._chord_to_text(mapping.chord)

            cmd_txts = []
            for cmd in mapping.commands:
                cmd_txts.append(Text._command_to_text(cmd, layout))

            lines.append(f"{notation} = {' '.join(cmd_txts)}")

        f.write("\n".join(lines))

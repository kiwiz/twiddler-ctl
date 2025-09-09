from typing import BinaryIO
from io import BytesIO
from ..models import Config, Chord, Command, Mapping, CommandType
from . import Serdes
import struct

HEADER_LENGTH = 0x80
MAPPING_LENGTH = 8
NONE_COMMAND = b"\x00\x00\x00\x00"


class Config7(Serdes):
    @staticmethod
    def _chord_from_bytes(data: bytes) -> Chord:
        value = struct.unpack("<I", data)[0]
        return Chord(
            thumbs=(
                bool(value & (1 << 0x13)),
                bool(value & (1 << 0x00)),
                bool(value & (1 << 0x04)),
                bool(value & (1 << 0x08)),
                bool(value & (1 << 0x0C)),
            ),
            fingers=(
                (
                    bool(value & (1 << 0x10)),
                    bool(value & (1 << 0x11)),
                    bool(value & (1 << 0x12)),
                ),
                (
                    bool(value & (1 << 0x01)),
                    bool(value & (1 << 0x02)),
                    bool(value & (1 << 0x03)),
                ),
                (
                    bool(value & (1 << 0x05)),
                    bool(value & (1 << 0x06)),
                    bool(value & (1 << 0x07)),
                ),
                (
                    bool(value & (1 << 0x09)),
                    bool(value & (1 << 0x0A)),
                    bool(value & (1 << 0x0B)),
                ),
                (
                    bool(value & (1 << 0x0D)),
                    bool(value & (1 << 0x0E)),
                    bool(value & (1 << 0x0F)),
                ),
            ),
        )

    @staticmethod
    def _chord_to_int(c: Chord) -> int:
        value = 0

        value |= int(c.thumbs[0]) << 0x13
        value |= int(c.thumbs[1]) << 0x00
        value |= int(c.thumbs[2]) << 0x04
        value |= int(c.thumbs[3]) << 0x08
        value |= int(c.thumbs[4]) << 0x0C

        value |= int(c.fingers[0][0]) << 0x10
        value |= int(c.fingers[0][1]) << 0x11
        value |= int(c.fingers[0][2]) << 0x12

        value |= int(c.fingers[1][0]) << 0x01
        value |= int(c.fingers[1][1]) << 0x02
        value |= int(c.fingers[1][2]) << 0x03

        value |= int(c.fingers[2][0]) << 0x05
        value |= int(c.fingers[2][1]) << 0x06
        value |= int(c.fingers[2][2]) << 0x07

        value |= int(c.fingers[3][0]) << 0x09
        value |= int(c.fingers[3][1]) << 0x0A
        value |= int(c.fingers[3][2]) << 0x0B

        value |= int(c.fingers[4][0]) << 0x0D
        value |= int(c.fingers[4][1]) << 0x0E
        value |= int(c.fingers[4][2]) << 0x0F

        return value

    @staticmethod
    def _chord_to_bytes(c: Chord) -> bytes:
        return struct.pack("<I", Config7._chord_to_int(c))

    @staticmethod
    def _command_from_bytes(data: bytes) -> Command:
        cmd_type, a, b = struct.unpack("<BHB", data)
        return Command(CommandType(cmd_type), a, b)

    @staticmethod
    def _command_to_bytes(cmd: Command) -> bytes:
        return struct.pack("<BHB", cmd.command_type, cmd.a, cmd.b)

    @staticmethod
    def _command_list_from_stream(fh: BinaryIO) -> list[Command]:
        commands: list[Command] = []

        while True:
            chunk = fh.read(4)
            if len(chunk) < 4:
                raise ValueError("Unexpected end of file while reading commands")
            if chunk == NONE_COMMAND:
                break

            commands.append(Config7._command_from_bytes(chunk))

        return commands

    @staticmethod
    def _command_list_to_bytes(commands: list[Command]) -> bytes:
        out = BytesIO()

        for cmd in commands:
            out.write(Config7._command_to_bytes(cmd))
        out.write(NONE_COMMAND)

        return out.getvalue()

    @staticmethod
    def read(fh: BinaryIO, layout: str) -> Config:
        cfg = Config()

        header = fh.read(HEADER_LENGTH)
        cfg.version = header[4]
        if cfg.version != 7:
            raise ValueError(f"Unsupported version: {cfg.version}, expected 7")

        a = header[5]
        cfg.repeat = bool(a & (1 << 0))
        cfg.bluetooth = bool(a & (1 << 1))
        cfg.direct = bool(a & (1 << 2))
        cfg.haptic = bool(a & (1 << 3))
        cfg.sticky_num = bool(a & (1 << 4))
        cfg.sticky_alt = bool(a & (1 << 5))
        cfg.sticky_ctrl = bool(a & (1 << 6))
        cfg.sticky_shift = bool(a & (1 << 7))

        b = header[6]
        cfg.nav_up_direction = b & 0x3
        cfg.nav_invert_x = bool(b & (1 << 2))
        cfg.nav_sensitivity = (b >> 3) & 0x7

        mapping_count, cfg.idle_time = struct.unpack("<2H", header[8:12])
        cfg.repeat_delay = header[12]

        cfg.dedicated = header[0x40 : 0x40 + 20]
        cfg.mappings = []
        for _ in range(mapping_count):
            chunk = fh.read(MAPPING_LENGTH)
            if len(chunk) < MAPPING_LENGTH:
                raise ValueError("Unexpected end of file while reading mappings")

            chord = Config7._chord_from_bytes(chunk[:4])
            command = Config7._command_from_bytes(chunk[4:])

            commands = [command]
            if command.command_type == CommandType.COMMAND_LIST:
                pos = fh.tell()
                fh.seek(HEADER_LENGTH + mapping_count * MAPPING_LENGTH + command.a)
                commands = Config7._command_list_from_stream(fh)
                fh.seek(pos)

            cfg.mappings.append(Mapping(chord, commands))

        return cfg

    @staticmethod
    def write(cfg: Config, fh: BinaryIO, layout: str) -> None:
        header = bytearray(HEADER_LENGTH)
        header[4] = cfg.version
        header[5] = (
            (int(cfg.repeat) << 0)
            | (int(cfg.bluetooth) << 1)
            | (int(cfg.direct) << 2)
            | (int(cfg.haptic) << 3)
            | (int(cfg.sticky_num) << 4)
            | (int(cfg.sticky_alt) << 5)
            | (int(cfg.sticky_ctrl) << 6)
            | (int(cfg.sticky_shift) << 7)
        )
        header[6] = (
            ((cfg.nav_up_direction & 0x3) << 0)
            | (int(cfg.nav_invert_x) << 2)
            | ((cfg.nav_sensitivity & 0x7) << 3)
        )

        header[8:12] = struct.pack("<2H", len(cfg.mappings), cfg.idle_time)
        header[12] = cfg.repeat_delay

        header[0x40 : 0x40 + 20] = cfg.dedicated
        header[0x60:0x80] = (
            b"\x00\x01\x02\x03\x04\x05\x06\x07"
            b"\x08\x09\x0a\x0c\x0d\x0f\x11\x14"
            b"\x16\x18\x1a\x1d\x80\x80\x80\x80"
            b"\x80\x80\x80\x80\x80\x80\x80\x80"
        )

        fh.write(header)

        base = HEADER_LENGTH + len(cfg.mappings) * MAPPING_LENGTH
        off = 0
        commands_map: dict[bytes, int] = {}

        mappings = sorted(cfg.mappings, key=lambda m: Config7._chord_to_int(m.chord))

        for mapping in mappings:
            fh.write(Config7._chord_to_bytes(mapping.chord))
            if len(mapping.commands) == 1:
                fh.write(Config7._command_to_bytes(mapping.commands[0]))
                continue

            buf = Config7._command_list_to_bytes(mapping.commands)
            existing_off = commands_map.get(buf)
            if existing_off is not None:
                fh.write(
                    Config7._command_to_bytes(
                        Command(CommandType.COMMAND_LIST, existing_off, 0)
                    )
                )
                continue

            fh.write(
                Config7._command_to_bytes(Command(CommandType.COMMAND_LIST, off, 0))
            )
            pos = fh.tell()
            fh.seek(base + off)
            fh.write(buf)
            commands_map[buf] = off
            off = fh.tell() - base
            fh.seek(pos)

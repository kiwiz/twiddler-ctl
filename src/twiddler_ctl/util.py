import functools
import layouts


_layouts = layouts.Layouts()


def normalize_str(val: str) -> str:
    return val.strip().replace(" ", "_").lower()


def _ignore(i: int) -> bool:
    return i >= 0xF0 and i <= 0x121


LAYOUT_MAP = {normalize_str(v): v for v in _layouts.list_layouts()}


@functools.cache
def get_forward_mapping(name: str, consumer: bool = False) -> dict | None:
    key = LAYOUT_MAP.get(name)
    if key is None:
        return None

    table = "to_hid_consumer" if consumer else "to_hid_keyboard"

    mapping = {}
    for k, v in _layouts.get_layout(key).dict(table).items():
        code = int(k, 16)
        if _ignore(code):
            continue

        mapping[code] = normalize_str(v)

    return mapping


@functools.cache
def get_backward_mapping(name: str, consumer: bool = False) -> dict | None:
    key = LAYOUT_MAP.get(name)
    if key is None:
        return None

    table = "from_hid_consumer" if consumer else "from_hid_keyboard"

    mapping = {}
    for k, v in _layouts.get_layout(key).dict(table).items():
        code = int(v, 16)
        if _ignore(code):
            continue

        mapping[normalize_str(k)] = code

    return mapping


def layout_exists(name: str) -> dict | None:
    return LAYOUT_MAP.get(name) is not None

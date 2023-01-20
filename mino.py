from enum import *

class _MinoType(Enum):
    PLACEMENT = 1
    LINECLEAR = 2
    NORMAL = 3

class _MinoColor(IntEnum):
    black = 0
    cyan = 1
    orange = 2
    yellow = 3
    red = 4
    magenta = 5
    blue = 6
    green = 7
    gray = 8

class _MinoName(IntEnum):
    _ = 0
    I = 1
    L = 2
    O = 3
    Z = 4
    T = 5
    J = 6
    S = 7
    G = 8

class Mino:
    def __init__(self, name=_MinoName._, type=_MinoType.NORMAL):
        self._mino = _MinoName(name)
        self._type = _MinoType(type)

    def type(self):
        return self._type.value

    def name(self):
        return self._mino.name

    def value(self):
        return self._mino.value

    def color(self):
        return _MinoColor(self._mino.value).name

    def is_empty(self):
        return self._mino.value == 0

    def next(self):
        return Mino((self._mino + 1) % len(_MinoName), self._type)

    def prev(self):
        return Mino((self._mino - 1) % len(_MinoName), self._type)

    def lineclear(self):
        self._type = _MinoType.LINECLEAR

    def unclear(self):
        self._type = _MinoType.NORMAL


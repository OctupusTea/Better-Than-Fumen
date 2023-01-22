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
    @staticmethod
    def count():
        return len(_MinoName)

    @staticmethod
    def copy(mino):
        return Mino(mino._name, mino._type)

    def __init__(self, name=_MinoName._, type=_MinoType.NORMAL):
        self._name = _MinoName(name)
        self._type = _MinoType(type)

    def set_mino(self, mino):
        self._name = mino._name
        self._type = mino._type

    def type(self, type=None):
        if type is None:
            return self._type.value
        else:
            self._type = _MinoType(type)

    def name(self, name=None):
        if name is None:
            return self._name.name
        else:
            self._name = _MinoName(name)

    def value(self, value=None):
        if value is None:
            return self._name.value
        else:
            self._name = _MinoName(value)

    def color(self):
        return _MinoColor(self._name.value).name

    def is_empty(self):
        return self._name.value == 0

    def to_next(self):
        self._name = _MinoName((self._name + 1) % len(_MinoName))
        return self

    def to_prev(self):
        self._name = _MinoName((self._name - 1) % len(_MinoName))
        return self


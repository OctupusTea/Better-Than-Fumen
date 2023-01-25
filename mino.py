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

    def fill_color(self):
        if self._name is _MinoName._:
            return 'black'
        elif self._name is _MinoName.G:
            return 'gray' + str(125 - self._type.value * 25)
        else:
            return _MinoColor(self._name.value).name + str(self._type.value)

    def outline_color(self):
        return 'gray' + str(100 - self._type.value* 25)

    def is_empty(self):
        return self._name.value == 0

    def to_next(self):
        self._name = _MinoName((self._name + 1) % len(_MinoName))
        return self

    def to_prev(self):
        self._name = _MinoName((self._name - 1) % len(_MinoName))
        return self

    def lineclear(self):
        if self._type is not _MinoType.PLACEMENT:
            self._type = _MinoType.LINECLEAR

    def unclear(self):
        if self._type is not _MinoType.PLACEMENT:
            self._type = _MinoType.NORMAL

    def toggle_lineclear(self):
        if self._type is _MinoType.NORMAL:
            self._type = _MinoType.LINECLEAR
        elif self._type is _MinoType.LINECLEAR:
            self._type = _MinoType.NORMAL

class PlacementTetromino:
    TETROMINO_SHAPE = {
        'I': [
            {(-1, 0), (0, 0), (1, 0), (2, 0)},
            {(0, -1), (0, 0), (0, 1), (0, 2)},
            {(-2, 0), (-1, 0), (0, 0), (1, 0)},
            {(0, -2), (0, -1), (0, 0), (0, 1)}
        ],
        'L': [
            {(-1, 0), (0, 0), (1, 0), (1, -1)},
            {(0, -1), (0, 0), (0, 1), (1, 1)},
            {(-1, 1), (-1, 0), (0, 0), (1, 0)},
            {(-1, -1), (0, -1), (0, 0), (0, 1)}
        ],
        'O': [
            {(0, -1), (0, 0), (1, -1), (1, 0)},
            {(0, -1), (0, 0), (1, -1), (1, 0)},
            {(0, -1), (0, 0), (1, -1), (1, 0)},
            {(0, -1), (0, 0), (1, -1), (1, 0)}
        ],
        'Z': [
            {(-1, -1), (0, -1), (0, 0), (1, 0)},
            {(1, -1), (1, 0), (0, 0), (0, 1)},
            {(-1, 0), (0, 0), (0, 1), (1, 1)},
            {(0, -1), (0, 0), (-1, 0), (-1, 1)}
        ],
        'T': [
            {(-1, 0), (0, 0), (1, 0), (0, -1)},
            {(0, -1), (0, 0), (0, 1), (1, 0)},
            {(-1, 0), (0, 0), (1, 0), (0, 1)},
            {(0, -1), (0, 0), (0, 1), (-1, 0)}
        ],
        'J': [
            {(-1, -1), (-1, 0), (0, 0), (1, 0)},
            {(1, -1), (0, -1), (0, 0), (0, 1)},
            {(-1, 0), (0, 0), (1, 0), (1, 1)},
            {(0, -1), (0, 0), (0, 1), (-1, 1)}
        ],
        'S': [
            {(-1, 0), (0, 0), (0, -1), (1, -1)},
            {(0, -1), (0, 0), (1, 0), (1, 1)},
            {(-1, 1), (0, 1), (0, 0), (1, 0)},
            {(-1, -1), (-1, 0), (0, 0), (0, 1)}
        ]
    }

    def __init__(self, field, name, rotation):
        self._mino = Mino(name, _MinoType.PLACEMENT)
        self._field = field

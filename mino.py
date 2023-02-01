from enum import *
from tkinter import StringVar

class _MinoType(Enum):
    PLACEMENT = 1
    LINECLEAR = 2
    NORMAL = 3
    GHOST = 4

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

    def reset(self):
        self._name = _MinoName._
        self._type = _MinoType.NORMAL

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
        if self._type is _MinoType.PLACEMENT:
            return 'gray25'
        else:
            return 'gray25'

    def is_empty(self):
        return self._name is _MinoName._

    def is_mino(self):
        return (self._name is not _MinoName._) and (self._name is not _MinoName.G)

    def is_placement(self):
        return self._type is _MinoType.PLACEMENT

    def is_ghost(self):
        return self._type is _MinoType.GHOST

    def is_placeable(self):
        return self.is_empty() or self.is_placement() or self.is_ghost()

    def to_prev(self):
        self._name = _MinoName((self._name - 1) % len(_MinoName))
        return self

    def to_next(self):
        self._name = _MinoName((self._name + 1) % len(_MinoName))
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
    ROTATIONS = ['0', 'R', '2', 'L']
    # ROTATIONS = ['SP', 'CW', '180', 'CCW']
    SHAPES = {
        '_': [],
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
        ],
        'G': []
    }

    def __init__(self, mino_value=0, x=0, y=0, rotation=0):
        self._mino = Mino(mino_value)
        self._x = x
        self._y = y
        self._rotation = rotation
        self._rotation_strvar = StringVar()
        self._update_strvar()

    def place(self, x, y, rotation=None):
        self._x = x
        self._y = y
        self.rotate(rotation)

    def _update_strvar(self):
        if self._rotation_strvar is not None:
            self._rotation_strvar.set(self.ROTATIONS[self._rotation])

    def rotation_strvar(self):
        return self._rotation_strvar

    def mino_value(self, value=None):
        if value is None:
            return self._mino.value()
        else:
            self._mino.value(value)

    def placement(self):
        return self._x, self._y

    def placement_tests(self, x, y):
        return [(x+dx, y+dy) for dx, dy in self.SHAPES[self._mino.name()][self._rotation]] if self._mino.is_mino() else []

    def rotate(self, rotation):
        self._rotation = self._rotation if rotation is None else rotation
        self._update_strvar()

    def rotation(self):
        return self._rotation

    def rotation_str(self):
        return self.ROTATIONS[self._rotation]

    def to_prev(self):
        self._mino_to_prev()
        return self

    def to_next(self):
        self._mino.to_next()
        return self

    def to_prev_rotation(self):
        self._rotation = (self._rotation - 1) % len(self.ROTATIONS)
        self._update_strvar()
        return self

    def to_next_rotation(self):
        self._rotation = (self._rotation + 1) % len(self.ROTATIONS)
        self._update_strvar()
        return self



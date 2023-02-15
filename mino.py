import dataclasses
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from tkinter import StringVar

from common import MinoType, MinoColor, MinoName, Pos

@dataclass
class Mino:
    name: MinoName = field(default=MinoName._)
    type: MinoType = field(default=MinoType.NORMAL)

    @staticmethod
    def count():
        return len(MinoName)

    def reset(self):
        self.name = MinoName._
        self.type = MinoType.NORMAL

    def set_mino(self, other):
        self.name = other.name
        self.type = other.type

    def fumen_name(self):
        return '_' if self.is_placeable() else\
                'X' if self.name is MinoName.G else self.name.name

    def value(self, value=None):
        return self.name.value

    def is_empty(self):
        return self.name is MinoName._

    def is_colored(self):
        return (self.name is not MinoName._) and (self.name is not MinoName.G)

    def is_placement(self):
        return self.type is MinoType.PLACEMENT

    def is_ghost(self):
        return self.type is MinoType.GHOST

    def is_placeable(self):
        return self.is_empty() or self.is_placement() or self.is_ghost()

    def fill_color(self):
        if self.name is MinoName._:
            return 'black'
        elif self.name is MinoName.G:
            return 'gray' + str(125 - self.type.value * 25)
        else:
            return MinoColor(self.name.value).name + str(self.type.value)

    def outline_color(self):
        if self.is_placement():
            return 'gray25'
        else:
            return 'gray25'

    def to_prev(self):
        self.name = MinoName((self.name - 1) % len(MinoName))
        return self

    def to_next(self):
        self.name = MinoName((self.name + 1) % len(MinoName))
        return self

    def lineclear(self):
        if self.type is not MinoType.PLACEMENT:
            self.type = MinoType.LINECLEAR

    def unclear(self):
        if self.type is not MinoType.PLACEMENT:
            self.type = MinoType.NORMAL

@dataclass
class PlacementTetromino:
    ROTATIONS = ['0', 'R', '2', 'L']
    # ROTATIONS = ['SP', 'CW', '180', 'CCW']
    FUMEN_ROTATIONS = ['spawn', 'right', 'reverse', 'left']
    SHAPES = {
        '_': [],
        'I': [
            [Pos(-1, 0), Pos(0, 0), Pos(1, 0), Pos(2, 0)],
            [Pos(0, -1), Pos(0, 0), Pos(0, 1), Pos(0, 2)],
            # [Pos(-2, 0), Pos(-1, 0), Pos(0, 0), Pos(1, 0)],
            [Pos(-1, 0), Pos(0, 0), Pos(1, 0), Pos(2, 0)],
            # [Pos(0, -2), Pos(0, -1), Pos(0, 0), Pos(0, 1)],
            [Pos(0, -1), Pos(0, 0), Pos(0, 1), Pos(0, 2)],
        ],
        'L': [
            [Pos(-1, 0), Pos(0, 0), Pos(1, 0), Pos(1, -1)],
            [Pos(0, -1), Pos(0, 0), Pos(0, 1), Pos(1, 1)],
            [Pos(-1, 1), Pos(-1, 0), Pos(0, 0), Pos(1, 0)],
            [Pos(-1, -1), Pos(0, -1), Pos(0, 0), Pos(0, 1)],
        ],
        'O': [
            [Pos(0, 0), Pos(0, 1), Pos(1, 0), Pos(1, 1)],
            [Pos(0, 0), Pos(0, 1), Pos(1, 0), Pos(1, 1)],
            [Pos(0, 0), Pos(0, 1), Pos(1, 0), Pos(1, 1)],
            [Pos(0, 0), Pos(0, 1), Pos(1, 0), Pos(1, 1)],
        ],
        'Z': [
            # [Pos(-1, -1), Pos(0, -1), Pos(0, 0), Pos(1, 0)],
            [Pos(-1, 0), Pos(0, 0), Pos(0, 1), Pos(1, 1)],
            [Pos(1, -1), Pos(1, 0), Pos(0, 0), Pos(0, 1)],
            [Pos(-1, 0), Pos(0, 0), Pos(0, 1), Pos(1, 1)],
            [Pos(1, -1), Pos(1, 0), Pos(0, 0), Pos(0, 1)],
            # [Pos(0, -1), Pos(0, 0), Pos(-1, 0), Pos(-1, 1)],
        ],
        'T': [
            [Pos(-1, 0), Pos(0, 0), Pos(1, 0), Pos(0, -1)],
            [Pos(0, -1), Pos(0, 0), Pos(0, 1), Pos(1, 0)],
            [Pos(-1, 0), Pos(0, 0), Pos(1, 0), Pos(0, 1)],
            [Pos(0, -1), Pos(0, 0), Pos(0, 1), Pos(-1, 0)],
        ],
        'J': [
            [Pos(-1, -1), Pos(-1, 0), Pos(0, 0), Pos(1, 0)],
            [Pos(1, -1), Pos(0, -1), Pos(0, 0), Pos(0, 1)],
            [Pos(-1, 0), Pos(0, 0), Pos(1, 0), Pos(1, 1)],
            [Pos(0, -1), Pos(0, 0), Pos(0, 1), Pos(-1, 1)],
        ],
        'S': [
            # [Pos(-1, 0), Pos(0, 0), Pos(0, -1), Pos(1, -1)],
            [Pos(-1, 1), Pos(0, 1), Pos(0, 0), Pos(1, 0)],
            # [Pos(0, -1), Pos(0, 0), Pos(1, 0), Pos(1, 1)],
            [Pos(-1, -1), Pos(-1, 0), Pos(0, 0), Pos(0, 1)],
            [Pos(-1, 1), Pos(0, 1), Pos(0, 0), Pos(1, 0)],
            [Pos(-1, -1), Pos(-1, 0), Pos(0, 0), Pos(0, 1)],
        ],
        'G': [],
    }

    mino: Mino = field(default=Mino(type=MinoType.PLACEMENT))
    pos: Pos = field(default_factory=Pos)
    rotation: int = field(default=0)
    coords: list = field(default_factory=list)
    direct_place: bool = field(default=False)
    placed: bool = field(default=False)
    placed_mino: Mino = field(default=Mino(type=MinoType.PLACEMENT))
    placed_pos: Pos = field(default_factory=Pos)
    placed_rotation: int = field(default=0)
    placed_coords: list = field(default_factory=list)
    rotation_strvar: StringVar = field(default_factory=StringVar)

    def __post_init__(self):
        self.gen_coords()
        self.update_strvar()

    def gen_coords(self, pos=None):
        pos = self.pos if pos is None else pos
        self.coords = [
                self.pos+dpos for dpos in self.SHAPES[self.mino.name.name][self.rotation]
        ] if self.mino.is_colored() else []

    def update_strvar(self):
        self.rotation_strvar.set(self.rotation_name())

    def place(self):
        self.placed = True
        self.placed_pos = Pos(*self.pos)
        self.placed_mino.set_mino(self.mino)
        self.placed_rotation = self.rotation
        self.placed_coords = self.coords[:]

    def clear(self):
        self.placed = False
        self.placed_coords.clear()

    def rotate(self, rotation):
        self.rotation = rotation if 0 <= rotation < len(self.ROTATIONS) else 0
        self.update_strvar()

    def rotation_name(self):
        return self.ROTATIONS[self.rotation]

    def to_prev_mino(self):
        self.mino.to_prev()
        return self

    def to_next_mino(self):
        self.mino.to_next()
        return self

    def to_prev_rotation(self):
        self.rotation = (self.rotation - 1) % len(self.ROTATIONS)
        self.update_strvar()
        return self

    def to_next_rotation(self):
        self.rotation = (self.rotation + 1) % len(self.ROTATIONS)
        self.update_strvar()
        return self

    def to_fumen_operation_args(self):
        return (self.placed_mino.name.name, self.FUMEN_ROTATIONS[self.placed_rotation],
                self.placed_pos.x, 19-self.placed_pos.y)


import dataclasses
from dataclasses import dataclass, field
from enum import *

class MinoType(Enum):
    PLACEMENT = 1
    LINECLEAR = 2
    NORMAL = 3
    GHOST = 4

class MinoColor(IntEnum):
    black = 0
    cyan = 1
    orange = 2
    yellow = 3
    red = 4
    magenta = 5
    blue = 6
    green = 7
    gray = 8

class MinoName(IntEnum):
    _ = 0
    I = 1
    L = 2
    O = 3
    Z = 4
    T = 5
    J = 6
    S = 7
    G = 8

@dataclass
class Pos:
    x: int = field(default=0)
    y: int = field(default=0)

    def __add__(self, other):
        return Pos(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Pos(self.x-other.x, self.y-other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError('index should be 0 or 1')

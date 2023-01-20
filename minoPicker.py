from tkinter import ttk
from tkinter import *

from mino import Mino
from minoField import MinoField

class MinoPicker(MinoField):
    def __init__(self, parent, mino_size):
        mino_size *= 2
        super().__init__(parent, mino_size, height=Mino.count(), width=1)
        self.unbind('<ButtonPress-1>')
        self.unbind('<B1-Motion')
        self.bind('<ButtonPress-1>', self._on_b1)
        for y in range(self._height):
            self._draw_mino(x=0, y=y, mino=Mino(y))

    def _on_b1(self, event):
        x = (event.x-1) // self._mino_size
        y = (event.y-1) // self._mino_size
        if 0 <= x < self._width and 0 <= y < self._height:
            MinoField._selected_mino = Mino(y)

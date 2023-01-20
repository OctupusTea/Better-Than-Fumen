from tkinter import ttk
from tkinter import *

from mino import Mino

class MinoField(Canvas):
    _selected_mino = Mino()
    _drawing_mino = Mino()

    @classmethod
    def next_mino(self, event):
        self._selected_mino = self._selected_mino.next()

    @classmethod
    def prev_mino(self, event):
        self._selected_mino = self._selected_mino.prev()

    @classmethod
    def _on_mousewheel(self, event):
        if event.delta < 0:
            self.prev_mino(event)
        else:
            self.next_mino(event)

    def __init__(self, parent, mino_size, height, width):
        super().__init__(parent, height=height*mino_size+1, width=width*mino_size+1 )
        self._height = height
        self._width = width
        self._mino_size = mino_size
        self._field=[[Mino()for j in range(height)] for i in range(width)]
        for i in range(width):
            for j in range(height):
                super().create_rectangle(i*mino_size, j*mino_size, (i+1)*mino_size, (j+1)*mino_size, fill='black', outline='gray25', width=3)
        self.bind('<ButtonPress-1>', self._on_b1)
        self.bind('<B1-Motion>', self._on_b1)
        self.bind('<ButtonRelease-1>', self._draw_reset)
        self.bind('<Button-5>', self.next_mino)
        self.bind('<Button-4>', self.prev_mino)
        self.bind('<MouseWheel>', self._on_mousewheel)

    def _on_b1(self, event):
        x = (event.x-1) // self._mino_size
        y = (event.y-1) // self._mino_size
        if 0 <= x < self._width and 0 <= y < self._height:
            if self._drawing_mino is None:
                self._drawing_mino = Mino() if self._selected_mino.value() == self._field[x][y].value() else self._selected_mino
            self._field[x][y] = self._drawing_mino
            self._draw_mino(x, y)

    def _draw_reset(self, event):
        self._drawing_mino = None

    def _draw_mino(self, x, y, mino=None):
        mino = self._drawing_mino if mino is None else mino
        color = mino.color() if mino.name() in ['_', 'G'] else mino.color() + str(mino.type())
        super().create_rectangle(x*self._mino_size, y*self._mino_size, (x+1)*self._mino_size, (y+1)*self._mino_size, fill=color, outline='gray25', width=3)

    def _check_lineclear(self, y):
        return all(mino != 0 for mino in _field[0:-1][y])


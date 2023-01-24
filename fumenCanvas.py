import math
from tkinter import ttk
from tkinter import *

from mino import *

# Base class for _MinoPicker and _MinoCanvas
class _MinoField(Canvas):
    def __init__(self, parent, mino_size, height, width, selected_mino, line_width=3):
        super().__init__(parent, height=height*mino_size+1, width=width*mino_size+1)
        self._height = height
        self._width = width
        self._mino_size = mino_size
        self._selected_mino = selected_mino
        self._line_width = line_width
        # internal mino state
        self._field=[[Mino()for y in range(height)] for x in range(width)]
        # canvas rectangles for later deletion
        self._rects=[[None for y in range(height)] for x in range(width)]
        # initial mino grid painting
        for x in range(width):
            for y in range(height):
                self._draw_mino(x, y, Mino())

    # convert event coordinates to mino coordinates
    def _event_coord(self, event):
        x = (event.x-1) // self._mino_size
        y = (event.y-1) // self._mino_size
        return x, y

    # test if mino coordinates are inside the field
    def _is_inside(self, x, y):
        return (0 <= x < self._width and 0 <= y < self._height)

    # draw [mino] on position [x] [y] of the field, with/without selected highlight (for _MinoPicker)
    def _draw_mino(self, x, y, mino, selected=False):
        if self._is_inside(x, y):
            # if [mino] is not '_', add modification to the rendered color
            color = mino.color()
            if mino.name() == 'G':
                color += str(125-mino.type()*25)
            elif mino.name() != '_':
                color += str(mino.type())
            # if the position is already occupied, delete the previous rectangle
            if self._rects[x][y] is not None:
                super().delete(self._rects[x][y])
            self._rects[x][y] = super().create_rectangle(
                    x*self._mino_size, y*self._mino_size,
                    (x+1)*self._mino_size, (y+1)*self._mino_size,
                    fill=color, outline=('white' if selected else 'gray25'), width=self._line_width
            )

    def resize(self, mino_size):
        # re-render only if the size actually changes
        if self._mino_size != mino_size:
            self._mino_size = mino_size
            super().config(height=self._height*mino_size+1, width=self._width*mino_size+1)
            for x in range(self._width):
                for y in range(self._height):
                    self._draw_mino(x, y, self._field[x][y])

# mino sketch board, for both normal and rising Fumen frames
class _MinoCanvas(_MinoField):
    def __init__(self, parent, mino_size, height, width, selected_mino):
        super().__init__(parent, mino_size, height, width, selected_mino)
        self._drawing_mino = None
        self._lineclear = [False for y in range(height)]

        self.bind('<ButtonPress-1>', self._on_b1)
        self.bind('<B1-Motion>', self._on_b1)
        self.bind('<ButtonRelease-1>', self._draw_reset)

    def _on_b1(self, event):
        x, y = self._event_coord(event)
        if self._is_inside(x, y):
            if self._drawing_mino is None:
                # set to eraser (mino '_') if the field mino is the same as the selected mino
                if self._field[x][y].value() == self._selected_mino.value():
                    self._drawing_mino = Mino()
                # just draw the selected mino otherwise
                else:
                    self._drawing_mino = Mino.copy(self._selected_mino)
            if self._field[x][y].value() != self._drawing_mino.value():
                self._field[x][y].value(self._drawing_mino.value())
                lineclear = self._check_lineclear(y)
                if lineclear != 0:
                    for x in range(self._width):
                        self._field[x][y].toggle_lineclear()
                        self._draw_mino(x, y, self._field[x][y])
                else:
                    self._draw_mino(x, y, self._field[x][y])

    # reset if the mouse button is released
    def _draw_reset(self, event):
        self._drawing_mino = None

    # check for lineclear at row [y]
    def _check_lineclear(self, y):
        lineclear = all(not column[y].is_empty() for column in self._field)
        if lineclear != self._lineclear[y]:
            self._lineclear[y] = lineclear
            return 1 if lineclear else -1
        else:
            return 0

# mino picker
class _MinoPicker(_MinoField):
    def __init__(self, parent, mino_size, selected_mino):
        super().__init__(parent, mino_size, Mino.count(), 1, selected_mino)
        self._previous_mino = Mino.copy(self._selected_mino)

        # pre-draw the mino color on the picker
        for y in range(Mino.count()):
            self._field[0][y] = Mino(y)
            self._draw_mino(0, y, self._field[0][y])

        self.bind('<ButtonPress-1>', self._on_b1)

    def _on_b1(self, event):
        x, y = self._event_coord(event)
        if self._is_inside(x, y):
            self._selected_mino.value(y)
            self.update_mino()

    # un-highlight the previously selected mino and highlight the current one
    def update_mino(self):
        self._draw_mino(0, self._previous_mino.value(), self._previous_mino)
        self._previous_mino.set_mino(self._selected_mino)
        self._draw_mino(0, self._selected_mino.value(), self._selected_mino, True)

# main Fumen canvas class
class FumenCanvas(Frame):
    # shared mino size across all instances
    _mino_size = 40

    def __init__(self, parent, mino_size):
        super().__init__(parent)
        self._selected_mino = Mino()

        self._main_frame = ttk.Frame(self, padding=2)
        self._main_frame.grid(column=1, row=0, sticky=(S,W))
        self._main_canvas = _MinoCanvas(
                self._main_frame,
                self._mino_size, 20, 10,
                self._selected_mino
        )
        self._main_canvas.grid()

        self._rise_frame = ttk.Frame(self, padding=2)
        self._rise_frame.grid(column=1, row=1, sticky=(N,W))
        self._rise_canvas = _MinoCanvas(
                self._rise_frame,
                self._mino_size, 1, 10,
                self._selected_mino
        )
        self._rise_canvas.grid()

        self._pick_frame = ttk.Frame(self, padding=2)
        self._pick_frame.grid(column=0, row=0, sticky=(S,E))
        self._pick_canvas = _MinoPicker(
                self._pick_frame,
                self._mino_size*1.5,
                self._selected_mino
        )
        self._pick_canvas.grid()

        self.bind_all('<Button-5>', self._on_mousewheel)
        self.bind_all('<Button-4>', self._on_mousewheel)
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.bind('<Configure>', self._on_resize)

    def _on_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            self._prev_mino()
        else:
            self._next_mino()
        self._pick_canvas.update_mino()

    def _prev_mino(self):
        self._selected_mino.to_prev()

    def _next_mino(self):
        self._selected_mino.to_next()

    def _on_resize(self, event):
        max_width = math.floor((event.width - 14) / 11.5)
        max_height = (event.height - 14) // 21
        self._mino_size = min(max_width, max_height)
        self._main_canvas.resize(self._mino_size)
        self._rise_canvas.resize(self._mino_size)
        self._pick_canvas.resize(self._mino_size*1.5)

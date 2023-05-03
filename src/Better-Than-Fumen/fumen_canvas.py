# -*- coding: utf-8 -*-

from tkinter import ttk, font, Frame, Canvas
from tkinter import E, W, S, N

from py_fumen_py import *
from py_fumen_py.constant import FieldConstants as Consts

from .config import CanvasConfig, KeyConfig

_config = CanvasConfig()
_keys = KeyConfig()
_selected_mino = Mino._
_operation = Operation()

class _BaseMinoCanvas(Canvas):
    """ _BaseMinoCanvas is the base class of MinoCanvas and MinoPicker.
    This base class provides the most basic functionalities for a mino canvas,
    such as painting minos, and resising of the canvas.
    Mino states should be handled by the derived classes, and thus not stored.
    """
    def __init__(self, parent, mino_size, height, width):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        mino_size: the mino size of this canvas
        height: the height of this canvas (in minos)
        width: the width of this canvas (in minos)
        """
        super().__init__(parent, height=height*mino_size,
                         width=width*mino_size)
        self._height = height
        self._width = width
        self._mino_size = mino_size

        self._rects = [[
                self.create_rectangle(
                    x*self._mino_size+2, y*self._mino_size+2,
                    (x+1)*self._mino_size, (y+1)*self._mino_size,
                    fill='black', outline='gray25', width=_config.LINE_WIDTH,
                ) for y in range(height)
            ] for x in range(width)
        ]

        self._texts = [[None for y in range(height)] for x in range(width)]

        def _event_coords(self.event):
            """Convert tkinter event coords to the mino grid coords."""
            return ((event.x-1)//self._mino_size,
                    (event.y-1)//self._mino_size)

        def _is_inside(self, x, y):
            """Check if a mino grid coords is inside this canvas."""
            return 0 <= x < self._width and 0 <= y < self._height

        def _paint_mino(self, x, y, fill, outline):
            """Paint mino at a given mino grid coords."""
            if self._is_inside(x, y):
                self.itemconfigure(
                    self._rects[x][y],
                    fill=fill,
                    outline=outline,
                )
            else:
                raise ValueError(f'Coords ({x}, {y}) is outside the canvas.')

        def _resize_at(self, x, y):
            """Resize the mino and the text at a given mino grid coords."""
            if self._is_inside(x, y):
                self.coords(
                    self._rects[x][y],
                    x*self._mino_size+2, y*self._mino_size+2,
                    (x+1)*self._mino_size, (y+1)*self._mino_size,
                )
                if self._texts[x][y] is not None:
                    self.coords(
                        self._texts[x][y],
                        (x+0.5)*self._mino_size,
                        (y+0.5)*self._mino_size,
                    )
                    self.itemconfigure(
                        self._texts[x][y],
                        font=(
                            "TkDefaultFont",
                            self._mino_size//2,
                            font.NORAML,
                        ),
                    )
                    self.tag_raise(self._texts[x][y], self._rects[x][y])
            else:
                raise ValueError(f'Coords ({x}, {y}) is outside the canvas.')

        def on_resize(self):
            """Resize the canvas objects if the whole canvas is resized."""
            if self._prev_mino_size != self._mino_size:
                self._prev_mino_size = self._mino_size
                self.config(height=self._height*self._mino_size,
                            width=self._width*self._mino_size)
                for x in range(self._width):
                    for y in range(self._height):
                        self._resize_at(x, y)
                return True
            return False

class MinoCanvas(ttk.Frame):
    """The canvas where the actual minos are drawn."""
    def __init__(self, parent, mino_size):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        mino_size: the mino size of this canvas
        """
        super().__init__(parent)
        self._field_frame = ttk.Frame(self, padding=2)
        self._field_frame.grid(column=0, row=0, sticky=(S,W))
        self._field_canvas = _BaseMinoCanvas(
            self._field_frame, mino_size,
            Consts.HEIGHT, Consts.WIDTH
        )
        self._garbage_frame = ttk.Frame(self, padding=2)
        self._garbage_frame.grid(column=0, row=1, sticky=(N,W))
        self._garbage_canvas = _BaseMinoCanvas(
            self._garbage_canvas, mino_size,
            Consts.GARBAGE_HEIGHT, Consts.WIDTH
        )

        self._field = Field()
        self._drawing_mino = None
        self._ghosts = []
        self._operations = []
        self._lineclear = [False for y in range(height)]

        self.bind(
            f'<{_keys.CANVAS_INVERT_MOD}-ButtonPress-{_keys.CANVAS_DRAW_BTN}>',
            self._on_inverted_draw
        )
        self.bind(
            f'<{_keys.CANVAS_INVERT_MOD}-B{_keys.CANVAS_DRAW_BTN}-Motion>',
            self._on_inverted_draw
        )
        self.bind(f'<ButtonPress-{_keys.CANVAS_DRAW_BTN}>', self._on_draw)
        self.bind(f'<B{_keys.CANVAS_DRAW_BTN}-Motion>', self._on_draw)
        self.bind(f'<ButtonRelease-{_keys.CANVAS_DRAW_BTN}>',
                  self._on_draw_reset)

    def _on_draw(self, event):
        pass

    def _on_inverted_draw(self, event):
        pass

    def _on_draw_reset(self, event):
        pass

    def _draw_mino(self, x, y):
        if [x, y] in _operation.shape():
            self._clear_operation()
        self._clear_ghosts()
        if self._drawing_mino is None:
            self._drawing_mino = (
                Mino._ if self._field.at(x, y) is _selected_mino
                else _selected_mino
            )

        if self._field.at(x, y) is not self._drawing_mino:
            self._field.at(x, y) = self._draw_mino
            self._check_lineclear_repaint(x, y)
        self._repaint_ghosts()

    def _draw_operation(self, x, y):
        pass

    def _check_lineclear_repaint(self, x, y):
        pass

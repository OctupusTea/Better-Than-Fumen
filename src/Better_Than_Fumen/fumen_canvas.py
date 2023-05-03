# -*- coding: utf-8 -*-

from tkinter import ttk, font, Frame, Canvas
from tkinter import E, W, S, N

from py_fumen_py import *
from py_fumen_py.constant import FieldConstants as Consts

from .config import CanvasConfig, KeyConfig

_config = CanvasConfig()
_keys = KeyConfig()
_selected_mino = Mino._
_placement = Operation()

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

    def _event_coords(self, event):
        """Convert tkinter event coords to the mino grid coords."""
        return ((event.x-1)//self._mino_size, (event.y-1)//self._mino_size)

    def _is_inside(self, x, y):
        """Check if a mino grid coords is inside this canvas."""
        return 0 <= x < self._width and 0 <= y < self._height

    def paint_mino_at(self, x, y, fill, outline):
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

class MinoCanvas(_BaseMinoCanvas):
    """The canvas where the actual minos are drawn."""
    def __init__(self, parent, mino_size):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        mino_size: the mino size of this canvas
        """
        super().__init__(parent, mino_size, Consts.TOTAL_HEIGHT, Consts.WIDTH)
        self.create_line(
            0, Consts.WIDTH*mino_size, mino_size, mino_size,
            fill='gray75', width=_config.LINE_WIDTH,
        )

        self._field = Field()
        self._drawing_mino = None
        self._ghosts = []
        self._placements = []
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

    def _event_coords(self, event):
        return ((event.x-1)//self._mino_size-1, (event.y-1)//self._mino_size-1)

    def _on_draw(self, event):
        pass

    def _on_inverted_draw(self, event):
        pass

    def _on_draw_reset(self, event):
        self._drawing_mino = None

    def _paint_mino(self, x, y, mino, type_='normal'):
        fill = ''.join((_config.FILL[mino], _config.HIGHLIGHT[type_]))
        self._garbage_canvas.paint_mino_at(
            x, y+1, fill, _config.OUTLINE['normal'])

    def repaint(self):
        self._clear_placements()
        for y in range(self._height):
            for x in range(self._width):
                self._paint_mino(x, y, self._field.at(x, y), 'normal')
            self._check_lineclear_repaint(0, y)

    def _draw_mino(self, x, y):
        if [x, y] in _placements:
            self._clear_placement()
        self._clear_ghosts()
        if self._drawing_mino is None:
            self._drawing_mino = (
                Mino._ if self._field.at(x, y) is _selected_mino
                else _selected_mino
            )

        if self._field.at(x, y) is not self._drawing_mino:
            self._field.fill(x, y, self._draw_mino)
            self._check_lineclear_repaint(x, y)
        self._repaint_ghosts()

    def _draw_placement(self, x, y):
        _placement.mino = _selected_mino
        _placement.x = x
        _placement.y = y
        if self._field.is_placeable(_placement):
            self._clear_placements()
            self._placements = _placement.shape()
            self._paint_placements()
            self._repaint_ghosts()

    def _check_lineclear_repaint(self, x, y):
        lineclear = all([px, y] in self._placements
                        or self._field.at(px, y) is not Mino._
                        for px in range(self._width))
        if y >= 0:
            if lineclear != self._lineclear[y]:
                self._lineclear[y] = lineclear
                repaint_list = [[x, y] for x in range(self._width)]
            else:
                repaint_list = [[x, y]]
            for x, y in repaint_list:
                if [x, y] in self._placements:
                    self._paint_mino(
                        x, y, _placement.mino, 'placement',
                    )
                else:
                    self._paint_mino(
                        x, y, self._field.at(x, y),
                        'lineclear' if lineclear else 'normal',
                    )
        else:
            self._paint_mino(x, y, self._field.at(x, y))

    def _clear_ghosts(self):
        for x, y in self._ghost_coords:
            if self._field.at(x, y) is Mino._:
                self._paint_mino(x, y, Mino._)
        self._ghost_coords.clear()

    def _repaint_ghosts(self):
        self._clear_ghosts()
        self._ghosts = self._field.drop(_placement, False).shape()
        for x, y in self._ghosts:
            if self._field.at(x, y) is Mino._:
                self._paint_mino(x, y, _placement.mino, 'ghost')

    def _clear_placements(self):
        placements = self._placements
        self._placements.clear()
        for x, y in placements:
            self._check_lineclear_repaint(x, y)
        self._clear_ghosts()

    def _paint_placements(self):
        for x, y in self._placements:
            if self._field.at(x, y) is Mino._:
                self._check_lineclear_repaint(x, y)

    def _shift_placements(self, dx, dy):
        for pos in self._placements:
            pos[0] += dx
            pos[1] += dy

        for pos in self._ghosts:
            pos[0] += dx
            pos[1] += dy

        if not all(self._is_inside(x, y) for x, y in self._placements):
            self._clear_placement()
        self._repaint_ghosts()

    def shift_up(self, amount=1):
        self._field.shift_up(amount)
        self._shift_placements(0, -amount)
        self.repaint()

    def shift_down(self, amount=1):
        self._field.shift_down(amount)
        self._shift_placements(0, amount)
        self.repaint()

    def shift_left(self, amount=1, warp=False):
        self._field.shift_left(amount, warp)
        self._shift_placements(-amount, 0)
        self.repaint()

    def shfit_right(self, amount=1, warp=False):
        self._field.shift_right(amount, warp)
        self._shift_placements(amount, 0)
        self.repaint()

    def field(self):
        return self._field.copy()

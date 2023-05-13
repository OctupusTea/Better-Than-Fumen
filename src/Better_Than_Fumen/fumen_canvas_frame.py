# -*- coding: utf-8 -*-

from math import floor
from tkinter import ttk, font, Frame, Canvas
from tkinter import E, W, S, N

from py_fumen_py import *
from py_fumen_py.constant import FieldConstants as Consts

from .config import CanvasConfig, KeyConfig

_config = CanvasConfig()
_keys = KeyConfig()

class _CanvasMode:
    mino = Mino._
    rotation = Rotation.SPAWN
    direct_place = False
    placement = None

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
            if self._rects[x][y] is not None:
                self.itemconfigure(
                    self._rects[x][y],
                    fill=fill,
                    outline=outline,
                )

    def set_text_at(self, x, y, text):
        """Alter text at a given mino grid coords."""
        if self._is_inside(x, y):
            if self._texts[x][y] is None:
                self._texts[x][y] = self.create_text(
                    (x+0.5)*self._mino_size, (y+0.5)*self._mino_size,
                    fill=_config.TEXT_COLOR,
                    font=(
                        "TkDefaultFont",
                        self._mino_size//2,
                        font.NORMAL
                    ),
                )
            self.itemconfigure(
                self._texts[x][y],
                text=text,
            )

    def _resize_at(self, x, y):
        """Resize the mino and the text at a given mino grid coords."""
        if self._is_inside(x, y):
            if self._rects[x][y] is not None:
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
                        font.NORMAL,
                    ),
                )
                if self._rects[x][y] is not None:
                    self.tag_raise(self._texts[x][y], self._rects[x][y])

    def on_resize(self, mino_size):
        """Resize the canvas objects if the whole canvas is resized."""
        if self._mino_size != mino_size:
            self._mino_size = mino_size
            self.config(height=self._height*self._mino_size,
                        width=self._width*self._mino_size)
            for x in range(self._width):
                for y in range(self._height):
                    self._resize_at(x, y)
            return True
        return False

class _FieldCanvas(_BaseMinoCanvas):
    """The canvas where the actual minos are drawn."""
    Y_TRANSFORM = {y: Consts.TOTAL_HEIGHT - y - 2
                   for y in range(-Consts.GARBAGE_HEIGHT, Consts.TOTAL_HEIGHT)}

    def __init__(self, parent, mino_size):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        mino_size: the mino size of this canvas
        """
        super().__init__(parent, mino_size, Consts.TOTAL_HEIGHT, Consts.WIDTH)
        self._garbage_separator = self.create_line(
            0, Consts.HEIGHT*mino_size+1,
            Consts.WIDTH*mino_size, Consts.HEIGHT*mino_size+1,
            fill='gray75', width=_config.LINE_WIDTH,
        )

        self._field = Field()
        self._drawing_mino = None
        self._ghosts = []
        self._placements = []
        self._lineclear = [False for y in range(Consts.HEIGHT)]

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
        return ((event.x-1)//self._mino_size,
                self.Y_TRANSFORM.get((event.y-1)//self._mino_size,
                                     Consts.HEIGHT+1))

    def _is_inside_field(self, x, y):
        return (0 <= x < self._width and
                -Consts.GARBAGE_HEIGHT <= y < Consts.HEIGHT)

    def _on_draw(self, event):
        x, y = self._event_coords(event)
        if _CanvasMode.direct_place and _CanvasMode.mino.is_colored():
            self._draw_placement(x, y)
        else:
            self._draw_mino(x, y)

    def _on_inverted_draw(self, event):
        x, y = self._event_coords(event)
        if _CanvasMode.direct_place or not _CanvasMode.mino.is_colored():
            self._draw_mino(x, y)
        else:
            self._draw_placement(x, y)

    def _on_draw_reset(self, event):
        self._drawing_mino = None

    def _paint_mino(self, x, y, mino, type_='normal'):
        self.paint_mino_at(
            x, self.Y_TRANSFORM[y],
            _config.mino_fill(mino, type_), _config.OUTLINE['normal']
        )

    def on_resize(self, mino_size):
        if super().on_resize(mino_size):
            self.coords(
                self._garbage_separator,
                0, Consts.HEIGHT*mino_size+1,
                Consts.WIDTH*mino_size, Consts.HEIGHT*mino_size+1,
            )

    def _draw_mino(self, x, y):
        if self._is_inside_field(x, y):
            if [x, y] in self._placements:
                self._clear_placements()
                _CanvasMode.placement = None
            self._clear_ghosts()
            if self._drawing_mino is None:
                self._drawing_mino = (
                    Mino._ if self._field.at(x, y) is _CanvasMode.mino
                    else _CanvasMode.mino
                )

            if self._field.at(x, y) is not self._drawing_mino:
                self._field.fill(x, y, self._drawing_mino)
                self._check_lineclear_repaint(x, y)
            self._repaint_ghosts()

    def _draw_placement(self, x, y):
        self._clear_placements()
        if _CanvasMode.mino.is_colored():
            _CanvasMode.placement = Operation(
                _CanvasMode.mino, _CanvasMode.rotation, x, y,
            )
        if (_CanvasMode.placement
                and self._field.is_placeable(_CanvasMode.placement)):
            self._placements = _CanvasMode.placement.shape()
            self._paint_placements()
            self._repaint_ghosts()
        else:
            _CanvasMode.placement = None

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
                        x, y, _CanvasMode.placement.mino, 'placement',
                    )
                else:
                    self._paint_mino(
                        x, y, self._field.at(x, y),
                        'lineclear' if lineclear else 'normal',
                    )
        else:
            self._paint_mino(x, y, self._field.at(x, y))

    def _clear_ghosts(self):
        for x, y in self._ghosts:
            if ([x, y] not in self._placements
                    and self._field.at(x, y) is Mino._):
                self._paint_mino(x, y, Mino._)
        self._ghosts.clear()

    def _repaint_ghosts(self):
        self._clear_ghosts()
        if _CanvasMode.placement:
            self._ghosts = self._field.drop(
                _CanvasMode.placement, False).shape()
        for x, y in self._ghosts:
            if ([x, y] not in self._placements
                    and self._field.at(x, y) is Mino._):
                self._paint_mino(x, y, _CanvasMode.placement.mino, 'ghost')

    def _clear_placements(self):
        placements = self._placements[:]
        self._placements.clear()
        for x, y in placements:
            self._check_lineclear_repaint(x, y)
        self._clear_ghosts()

    def _paint_placements(self):
        for x, y in self._placements:
            if self._field.at(x, y) is Mino._:
                self._check_lineclear_repaint(x, y)

    def _shift_repaint(self, dx, dy):
        self._clear_placements()
        self._clear_ghosts()
        for y in range(-Consts.GARBAGE_HEIGHT, Consts.HEIGHT):
            for x in range(self._width):
                self._paint_mino(x, y, self._field.at(x, y), 'normal')
            self._check_lineclear_repaint(0, y)
        if _CanvasMode.placement:
            _CanvasMode.placement.shift(dx, dy)
            if self._field.is_placeable(_CanvasMode.placement):
                self._placements = _CanvasMode.placement.shape()
                self._paint_placements()
                self._repaint_ghosts()
            else:
                _CanvasMode.placement = None

    def shift_up(self, amount=1):
        self._field.shift_up(amount)
        self._shift_repaint(0, amount)

    def shift_down(self, amount=1):
        self._field.shift_down(amount)
        self._shift_repaint(0, -amount)

    def shift_left(self, amount=1, warp=False):
        self._field.shift_left(amount, warp)
        self._shift_repaint(-amount, 0)

    def shift_right(self, amount=1, warp=False):
        self._field.shift_right(amount, warp)
        self._shift_repaint(amount, 0)

    def field(self):
        return self._field.copy()

class _MinoPickerCanvas(_BaseMinoCanvas):
    def __init__(self, parent, mino_size):
        super().__init__(parent, mino_size, len(Mino), 5)
        self._prev_selection = [4, 0]

        for y in Mino:
            for x in Rotation:
                if y.is_colored():
                    self._paint_mino(x, y)
                    self.set_text_at(x, y, x.short_name())
                else:
                    self.delete(self._rects[x][y])
            self._paint_mino(len(Rotation), y)

        self.bind(f'<ButtonPress-{_keys.PICKER_SELECT_BTN}>',
                  self._on_select_mino)

    def _on_select_mino(self, event):
        x, y = self._event_coords(event)
        if self._is_inside(x, y):
            _CanvasMode.mino = Mino(y)
            if x < len(Rotation) and _CanvasMode.mino.is_colored():
                _CanvasMode.direct_place = True
                _CanvasMode.rotation = Rotation(x)
            else:
                _CanvasMode.direct_place = False
                _CanvasMode.rotation = Rotation.SPAWN
            self.update_mino()

    def _paint_mino(self, x, y, selected=False):
        self.paint_mino_at(
            x, y, _config.mino_fill(y),
            _config.OUTLINE['selected' if selected else 'normal'])

    def update_mino(self):
        x, y = self._prev_selection
        self._paint_mino(x, y)
        self._paint_mino(len(Rotation), y)
        self._prev_selection = [
            _CanvasMode.rotation.value if _CanvasMode.mino.is_colored()
            else len(Rotation),
            _CanvasMode.mino.value,
        ]
        x, y = self._prev_selection
        self._paint_mino(x, y, True)
        if not _CanvasMode.direct_place:
            self._paint_mino(len(Rotation), y, True)

class FumenCanvasFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._field_frame = ttk.Frame(self, padding=2)
        self._field_frame.grid(column=1, row=0, rowspan=2, sticky=(S,W))
        self._field_canvas = _FieldCanvas(
            self._field_frame, _config.MINO_SIZE
        )
        self._field_canvas.grid()

        self._picker_frame = ttk.Frame(self, padding=2)
        self._picker_frame.grid(column=0, row=0, sticky=(S,E))
        self._picker_canvas = _MinoPickerCanvas(
            self._picker_frame,
            floor(_config.MINO_SIZE*_config.PICKER_SIZE_MULT)
        )
        self._picker_canvas.grid()
        self._picker_canvas.update_mino()

        self.bind_all(f'<{_keys.PICKER_WHEEL_MOD}-Button-4>',
                      self._on_rotation_scroll)
        self.bind_all(f'<{_keys.PICKER_WHEEL_MOD}-Button-5>',
                      self._on_rotation_scroll)
        self.bind_all(f'<{_keys.PICKER_WHEEL_MOD}-MouseWheel>',
                      self._on_rotation_scroll)
        self.bind_all('<Button-4>', self._on_mino_scroll)
        self.bind_all('<Button-5>', self._on_mino_scroll)
        self.bind_all('<MouseWheel>', self._on_mino_scroll)

        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Up>', self._on_shift_up)
        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Down>', self._on_shift_down)
        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Left>', self._on_shift_left)
        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Right>', self._on_shift_right)

        self.bind('<Configure>', self._on_resize)

    def _on_mino_scroll(self, event):
        if _keys.PICKER_WHEEL_ENABLED:
            if event.delta > 0 or event.num == 4:
                delta = 1
            else:
                delta = -1
            if _keys.PICKER_WHEEL_REVERSED:
                delta *= -1
            _CanvasMode.mino = _CanvasMode.mino.shifted(delta)
            self._picker_canvas.update_mino()

    def _on_rotation_scroll(self, event):
        if _keys.PICKER_WHEEL_ENABLED:
            if event.delta > 0 or event.num == 4:
                delta = 1
            else:
                delta = -1
            if _keys.PICKER_WHEEL_REVERSED:
                delta *= -1
            _CanvasMode.rotation = _CanvasMode.rotation.shifted(delta)
            self._picker_canvas.update_mino()

    def _on_shift_up(self, event):
        self._field_canvas.shift_up()

    def _on_shift_down(self, event):
        self._field_canvas.shift_down()

    def _on_shift_left(self, event):
        self._field_canvas.shift_left()

    def _on_shift_right(self, event):
        self._field_canvas.shift_right()

    def _on_resize(self, event):
        max_width = floor((event.width - 4)
            / (Consts.WIDTH + (len(Rotation)+1) * _config.PICKER_SIZE_MULT))
        max_height = (event.height - 4) // (Consts.TOTAL_HEIGHT)
        mino_size = min(max_width, max_height)
        self._field_canvas.on_resize(mino_size)
        self._picker_canvas.on_resize(
            floor(mino_size*_config.PICKER_SIZE_MULT))

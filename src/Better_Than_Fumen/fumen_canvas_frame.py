# -*- coding: utf-8 -*-

from copy import copy
from math import floor
from tkinter import ttk, font, Button, Canvas, Frame, Label
from tkinter import N, S, E, W
import tkinter as tk

from py_fumen_py import *
from py_fumen_py.action import Action
from py_fumen_py.constant import FieldConstants as Consts

from .config import CanvasConfig, KeyConfig

_config = CanvasConfig()
_keys = KeyConfig()

class _CanvasMode:
    """Static class for data interchange between classes within this module."""
    mino = Mino._
    rotation = Rotation.SPAWN
    direct_place = False
    placement = None

class _BaseMinoFrame(ttk.Frame):
    """ The base class of MinoCanvas and MinoPicker.
    Provide the most basic functionalities for a mino canvas.
    Mino states should be handled by the derived classes, and thus not stored.
    """
    def __init__(self, parent, mino_size, height, width, **kwargs):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        mino_size: the mino size of this canvas
        height: the height of this canvas (in minos)
        width: the width of this canvas (in minos)
        """
        super().__init__(parent, **kwargs)
        self._canvas = Canvas(self, height=height*mino_size,
                              width=width*mino_size)
        self._canvas.grid()
        self._height = height
        self._width = width
        self._mino_size = mino_size

        self._rects = [[
                self._canvas.create_rectangle(
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
                self._canvas.itemconfigure(
                    self._rects[x][y],
                    fill=fill,
                    outline=outline,
                )

    def set_text_at(self, x, y, text):
        """Alter text at a given mino grid coords."""
        if self._is_inside(x, y):
            if self._texts[x][y] is None:
                self._texts[x][y] = self._canvas.create_text(
                    (x+0.5)*self._mino_size, (y+0.5)*self._mino_size,
                    fill=_config.TEXT_COLOR,
                    font=_config.FONT,
                )
            self._canvas.itemconfigure(
                self._texts[x][y],
                text=text,
            )

    def _resize_at(self, x, y):
        """Resize the mino and the text at a given mino grid coords."""
        if self._is_inside(x, y):
            if self._rects[x][y]:
                self._canvas.coords(
                    self._rects[x][y],
                    x*self._mino_size+2, y*self._mino_size+2,
                    (x+1)*self._mino_size, (y+1)*self._mino_size,
                )
            if self._texts[x][y]:
                self._canvas.coords(
                    self._texts[x][y],
                    (x+0.5)*self._mino_size,
                    (y+0.5)*self._mino_size,
                )
                self._canvas.itemconfigure(
                    self._texts[x][y],
                    font=_config.FONT,
                )
            if self._texts[x][y] and self._rects[x][y]:
                self._canvas.tag_raise(self._texts[x][y], self._rects[x][y])

    def on_resize(self, mino_size):
        """Resize the canvas objects if the whole canvas is resized."""
        if self._mino_size != mino_size:
            self._mino_size = mino_size
            self._canvas.config(height=self._height*self._mino_size,
                                width=self._width*self._mino_size)
            for x in range(self._width):
                for y in range(self._height):
                    self._resize_at(x, y)
            return True
        return False

class _FieldCanvasFrame(_BaseMinoFrame):
    """The frame where the actual minos are drawn."""

    def __init__(self, parent, mino_size, **kwargs):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        mino_size: the mino size of this canvas
        """
        super().__init__(parent, mino_size,
            Consts.TOTAL_HEIGHT, Consts.WIDTH, **kwargs)
        self._garbage_separator = self._canvas.create_line(
            0, Consts.HEIGHT*mino_size+1,
            Consts.WIDTH*mino_size, Consts.HEIGHT*mino_size+1,
            fill='gray75', width=_config.LINE_WIDTH,
        )

        self._field = Field()
        self._drawing_mino = None
        self._ghosts = []
        self._placements = []
        self._lineclear = [False for y in range(Consts.HEIGHT)]

        self._canvas.bind(
            f'<{_keys.CANVAS_INVERT_MOD}-ButtonPress-{_keys.CANVAS_DRAW_BTN}>',
            self._on_inverted_draw
        )
        self._canvas.bind(
            f'<{_keys.CANVAS_INVERT_MOD}-B{_keys.CANVAS_DRAW_BTN}-Motion>',
            self._on_inverted_draw
        )
        self._canvas.bind(f'<ButtonPress-{_keys.CANVAS_DRAW_BTN}>',
                          self._on_draw)
        self._canvas.bind(f'<B{_keys.CANVAS_DRAW_BTN}-Motion>',
                          self._on_draw)
        self._canvas.bind(f'<ButtonRelease-{_keys.CANVAS_DRAW_BTN}>',
                          self._on_draw_reset)

    def _event_coords(self, event):
        """Convert tkinter event coords to the mino grid coords,
        and transform the y coord to match that in the Field class.
        """
        return ((event.x-1)//self._mino_size,
                Consts.TOTAL_HEIGHT-2-(event.y-1)//self._mino_size)

    def _is_inside_field(self, x, y):
        """Check if a mino grid coords is inside a Field."""
        return (0 <= x < self._width and
                -Consts.GARBAGE_HEIGHT <= y < Consts.HEIGHT)

    def _on_draw(self, event):
        """Draw event handler.
        The default behavior of most Fumen editors.
        Draw placement if the right-most column of the picker is not selected;
        otherwise, draw mino.
        """
        x, y = self._event_coords(event)
        if _CanvasMode.direct_place and _CanvasMode.mino.is_colored():
            self._draw_placement(x, y)
        else:
            self._draw_mino(x, y)

    def _on_inverted_draw(self, event):
        """Draw event handler (inverted).
        Draw mino if the right-most column of the picker is selected;
        otherwise, draw drawplacement.
        """
        x, y = self._event_coords(event)
        if _CanvasMode.direct_place or not _CanvasMode.mino.is_colored():
            self._draw_mino(x, y)
        else:
            self._draw_placement(x, y)

    def _on_draw_reset(self, event):
        """Reset the drawing mino when a drawing event ends."""
        self._drawing_mino = None

    def _paint_mino(self, x, y, mino, type_='normal'):
        """Retrieve the desired mino fill and outline for paint_mino_at()."""
        self.paint_mino_at(
            x, Consts.TOTAL_HEIGHT-2-y,
            _config.mino_fill(mino, type_), _config.OUTLINE['normal']
        )

    def on_resize(self, mino_size):
        """Call super().on_resize() to check if resizing happens,
        and resize the garbage separator accordingly.
        """
        if super().on_resize(mino_size):
            self._canvas.coords(
                self._garbage_separator,
                0, Consts.HEIGHT*mino_size+1,
                Consts.WIDTH*mino_size, Consts.HEIGHT*mino_size+1,
            )

    def _draw_mino(self, x, y):
        """Draw mino at the given mino grid coords.
        Remove placements if the coords are overlapping with the placement.
        Clear and repaint ghosts.
        """
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
        """Convert the event to an Operation and repaint placement."""
        if _CanvasMode.mino.is_colored():
            _CanvasMode.placement = Operation(
                _CanvasMode.mino, _CanvasMode.rotation, x, y,
            )
        self._repaint_placements()

    def _check_lineclear_repaint(self, x, y):
        """Check lineclear (and placements) at the given mino grid coords,
        and repaint accordingly.
        The garbage line(s) are not affected by lineclears.
        """
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

    def repaint(self):
        """Repaint the whole canvas, including placements and ghosts."""
        self._clear_placements()
        self._clear_ghosts()
        for y in range(-Consts.GARBAGE_HEIGHT, Consts.HEIGHT):
            for x in range(self._width):
                self._paint_mino(x, y, self._field.at(x, y), 'normal')
            self._check_lineclear_repaint(0, y)
        self._repaint_placements()

    def _clear_ghosts(self):
        """Remove painted ghosts and clear the list of ghost coords."""
        for x, y in self._ghosts:
            if ([x, y] not in self._placements
                    and self._field.at(x, y) is Mino._):
                self._paint_mino(x, y, Mino._)
        self._ghosts.clear()

    def _repaint_ghosts(self):
        """Clear ghosts, call Field.drop() to determine the ghost coords of
        the current placement, and paint ghosts accordingly.
        """
        self._clear_ghosts()
        if _CanvasMode.placement:
            self._ghosts = self._field.drop(
                _CanvasMode.placement, False).shape()
        for x, y in self._ghosts:
            if ([x, y] not in self._placements
                    and self._field.at(x, y) is Mino._):
                self._paint_mino(x, y, _CanvasMode.placement.mino, 'ghost')

    def _clear_placements(self):
        """Clear the painted placements and the list of placement coords.
        Also clear the ghosts and the list of ghost coords.
        """
        placements = self._placements[:]
        self._placements.clear()
        for x, y in placements:
            self._check_lineclear_repaint(x, y)
        self._clear_ghosts()

    def _repaint_placements(self):
        """Clear the painted placements and repaint.
        Reset the placement if it is not valid.
        """
        self._clear_ghosts()
        self._clear_placements()
        if _CanvasMode.placement:
            if self._field.is_placeable(_CanvasMode.placement):
                self._placements = _CanvasMode.placement.shape()
                for x, y in self._placements:
                    self._check_lineclear_repaint(x, y)
                self._repaint_ghosts()
            else:
                _CanvasMode.placement = None

    def _shift_placement_repaint(self, dx, dy):
        if _CanvasMode.placement:
            _CanvasMode.placement.shift(dx, dy)
        self.repaint()

    def shift_up(self, amount=1):
        self._field.shift_up(amount)
        self._shift_placement_repaint(0, amount)

    def shift_down(self, amount=1):
        self._field.shift_down(amount)
        self._shift_placement_repaint(0, -amount)

    def shift_left(self, amount=1, warp=False):
        self._field.shift_left(amount, warp)
        self._shift_placement_repaint(-amount, 0)

    def shift_right(self, amount=1, warp=False):
        self._field.shift_right(amount, warp)
        self._shift_placement_repaint(amount, 0)

    def field(self):
        return self._field.copy()

    def replace_field(self, field):
        self._field = field.copy()

class _MinoPickerFrame(_BaseMinoFrame):
    """The frame for mino and rotation selection."""
    def __init__(self, parent, mino_size, **kwargs):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        mino_size: the mino size of this canvas
        """
        super().__init__(parent, mino_size,
            len(Mino), len(Rotation)+1, **kwargs)
        self._prev_selection = [4, 0]

        for y in Mino:
            for x in Rotation:
                if y.is_colored():
                    self._paint_mino(x, y)
                else:
                    self.set_text_at(x, y, x.short_name())
                    self._canvas.delete(self._rects[x][y])
                    self._rects[x][y] = None
            self._paint_mino(len(Rotation), y)

        self._canvas.bind(f'<ButtonPress-{_keys.PICKER_SELECT_BTN}>',
                          self._on_select_mino)

    def _on_select_mino(self, event):
        """Event handler for mino selection.
        Update mino, rotation and direct_place in _CanvasMode.
        direct_place is reset if the right-most column is selected,
        and is set otherwise.
        direct_place determines whether placement or mino should be drawn
        when a click event happens within _FieldCanvas.
        """
        x, y = self._event_coords(event)
        if self._is_inside(x, y):
            _CanvasMode.mino = Mino(y)
            if x < len(Rotation) and _CanvasMode.mino.is_colored():
                _CanvasMode.direct_place = True
                _CanvasMode.rotation = Rotation(x)
            else:
                _CanvasMode.direct_place = False
                _CanvasMode.rotation = Rotation.SPAWN
            self.repaint()

    def _paint_mino(self, x, y, selected=False):
        """Retreieve the desired mino fill and outline for paint_mino_at()"""
        self.paint_mino_at(
            x, y, _config.mino_fill(
                y, type_='normal' if x == len(Rotation) else 'placement'
            ),
            _config.OUTLINE['selected' if selected else 'normal'])

    def repaint(self):
        """Repaint according to the new selection.
        The right-most column indicates if the direct_place mode is enabled.
        """
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

class _ControlPanelFrame(ttk.Frame):
    """The control panel for the fumen canvas."""
    def __init__(self, parent, unit_size, **kwargs):
        """Keyword arguments:
        parent: the parent of this canvas as a tkinter widget.
        unit_size: the displayeing unit size (mino_size of the canvas)
        """
        super().__init__(parent, **kwargs)
        self._unit_size = unit_size
        self._page_label = Label(
            self, text='Page 1/1', font=_config.FONT,
            relief='flat', borderwidth=_config.LINE_WIDTH,
        )
        self._page_label.grid(column=2, row=0, sticky=(N,S,E,W))

        self._first_button = Button(
            self, text='|<', font=_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._first_button.grid(column=0, row=0, sticky=(E,W))

        self._prev_button = Button(
            self, text='<<', font=_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._prev_button.grid(column=1, row=0, sticky=(E,W))

        self._next_button = Button(
            self, text='>>', font=_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._next_button.grid(column=3, row=0, sticky=(E,W))

        self._last_button = Button(
            self, text='>|', font=_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._last_button.grid(column=4, row=0, sticky=(E,W))

        self._delete_button = Button(
            self, text='Del', font=_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._delete_button.grid(
            column=1, row=1, sticky=(E,W)
        )

        self._copy_button = Button(
            self, text='Copy', font=_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._copy_button.grid(
            column=2, row=1, sticky=(E,W)
        )

        self._insert_button = Button(
            self, text='Ins', font=_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._insert_button.grid(
            column=3, row=1, sticky=(E,W)
        )

    def update_page_label(self, current, total):
        self._page_label.config(text=f'Page {current+1}/{total}')

    def bind_page_flips(self, prev, next_, first, last, delete, copy, insert):
        self._prev_button.config(command=prev)
        self._next_button.config(command=next_)
        self._first_button.config(command=first)
        self._last_button.config(command=last)
        self._delete_button.config(command=delete)
        self._copy_button.config(command=copy)
        self._insert_button.config(command=insert)

    def on_resize(self, unit_size):
        self._unit_size = unit_size
        self._page_label.config(font=_config.FONT)
        self._first_button.config(font=_config.FONT)
        self._prev_button.config(font=_config.FONT)
        self._next_button.config(font=_config.FONT)
        self._last_button.config(font=_config.FONT)
        self._insert_button.config(font=_config.FONT)
        self._delete_button.config(font=_config.FONT)

class FumenCanvasFrame(ttk.Frame):
    """The tkinter frame extension for the Fumen drawing canvas."""
    def __init__(self, parent):
        super().__init__(parent)

        _config.FONT = font.nametofont(f'Tk{_config.FONT_STYLE}Font')
        _config.FONT.config(size=_config.MINO_SIZE//2)

        self._field_frame = _FieldCanvasFrame(
            self, _config.MINO_SIZE, padding=2
        )
        self._field_frame.grid(column=1, row=0, rowspan=2, sticky=(S,W))

        self._picker_frame = _MinoPickerFrame(
            self, floor(_config.MINO_SIZE*_config.PICKER_SIZE_MULT), padding=2
        )
        self._picker_frame.grid(column=0, row=1, sticky=(S,E))
        self._picker_frame.repaint()

        self._control_frame = _ControlPanelFrame(
            self, _config.MINO_SIZE, padding=2
        )
        self._control_frame.grid(column=0, row=0, sticky=(S,E))
        self._control_frame.bind_page_flips(
            self._prev_page, self._next_page,
            self._first_page, self._last_page,
            self._delete_page, self._copy_page, self._insert_page,
        )

        self._pages = [Page(field=Field(), flags=Flags())]
        self._current_page = 0
        self._to_page(0)

        self.bind_all(f'<{_keys.PICKER_WHEEL_MOD}-Button-4>',
                      self._on_rotation_scroll)
        self.bind_all(f'<{_keys.PICKER_WHEEL_MOD}-Button-5>',
                      self._on_rotation_scroll)
        self.bind_all(f'<{_keys.PICKER_WHEEL_MOD}-MouseWheel>',
                      self._on_rotation_scroll)
        self.bind_all('<Button-4>', self._on_mino_scroll)
        self.bind_all('<Button-5>', self._on_mino_scroll)
        self.bind_all('<MouseWheel>', self._on_mino_scroll)

        self.bind_all(f'<{_keys.FUMEN_PAGEDOWN}>', self._next_page)
        self.bind_all(f'<{_keys.FUMEN_PAGEUP}>', self._prev_page)
        self.bind_all(f'<{_keys.FUMEN_FIRST}>', self._first_page)
        self.bind_all(f'<{_keys.FUMEN_LAST}>', self._last_page)

        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Up>', self._on_shift_up)
        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Down>', self._on_shift_down)
        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Left>', self._on_shift_left)
        self.bind(f'<{_keys.CANVAS_SHIFT_MOD}-Right>', self._on_shift_right)

        self.bind('<Configure>', self._on_resize)

    def _on_mino_scroll(self, event):
        """Event handler for scrolling wihtout a modifier key.
        Switch to the next or the previous mino if scrolling is enabled.
        """
        if _keys.PICKER_WHEEL_ENABLED:
            if event.delta > 0 or event.num == 5:
                delta = 1
            else:
                delta = -1
            if _keys.PICKER_WHEEL_REVERSED:
                delta *= -1
            _CanvasMode.mino = _CanvasMode.mino.shifted(delta)
            self._picker_frame.repaint()

    def _on_rotation_scroll(self, event):
        """Event handler for scrolling with the desired modifier key.
        Switch to the next or the previous rotation if scrolling is enabled.
        """
        if _keys.PICKER_WHEEL_ENABLED:
            if event.delta > 0 or event.num == 5:
                delta = 1
            else:
                delta = -1
            if _keys.PICKER_WHEEL_REVERSED:
                delta *= -1
            _CanvasMode.rotation = _CanvasMode.rotation.shifted(delta)
            self._picker_frame.repaint()

    def _save_current_page(self):
        """Save the _FieldCanvas to the viewed page."""
        page = self._pages[self._current_page]
        page.field = self._field_frame.field()
        page.operation = copy(_CanvasMode.placement)

    def _to_page(self, page):
        """Load page to _FieldCanvas."""
        self._current_page = page
        self._field_frame.replace_field(self._pages[page].field)
        _CanvasMode.placement = self._pages[page].operation
        self._field_frame.repaint()
        self._control_frame.update_page_label(page, len(self._pages))

    def _next_page(self, event=None):
        """Switch to the next page.
        Add a new page if the current page is the last page."""
        self._save_current_page()
        page = self._current_page + 1
        if page >= len(self._pages):
            last_page = self._pages[-1]
            field = last_page.field.copy()
            field.apply_action(Action(
                last_page.operation if last_page.operation
                else Operation(Mino._, Rotation.REVERSE, 0, Consts.HEIGHT-1),
                last_page.flags.rise,
                last_page.flags.mirror,
                None,
                None,
                last_page.flags.lock,
            ))
            self._pages.append(Page(
                field=field,
                flags=copy(last_page.flags),
                comment=last_page.comment,
            ))
        self._to_page(page)

    def _prev_page(self, event=None):
        """Switch to the previous page.
        Do nothing if the current page is the first page."""
        self._save_current_page()
        page = self._current_page - 1
        if page >= 0:
            self._to_page(page)

    def _first_page(self, event=None):
        self._save_current_page()
        self._to_page(0)

    def _last_page(self, event=None):
        self._save_current_page()
        self._to_page(len(self._pages)-1)

    def _delete_page(self, event=None):
        if len(self._pages) > 1:
            del self._pages[self._current_page]
            self._to_page(max(0, self._current_page-1))

    def _copy_page(self, event=None):
        self._save_current_page()
        copied_page = self._pages[self._current_page]
        self._pages.insert(self._current_page, Page(
            field=copied_page.field.copy(),
            operation=copied_page.operation.shifted(0, 0)
                      if copied_page.operation else None,
            flags=Flags(
                lock=False,
                mirror=False,
                colorize=copied_page.flags.colorize,
                rise=False,
                quiz=copied_page.flags.quiz,
            ),
            comment=copied_page.comment
        ))
        self._to_page(self._current_page)

    def _insert_page(self, event=None):
        self._save_current_page()
        self._pages.insert(self._current_page, Page(
            field=Field(),
            flags=Flags(),
        ))
        self._to_page(self._current_page)

    def _on_shift_up(self, event):
        self._field_frame.shift_up()

    def _on_shift_down(self, event):
        self._field_frame.shift_down()

    def _on_shift_left(self, event):
        self._field_frame.shift_left()

    def _on_shift_right(self, event):
        self._field_frame.shift_right()

    def _on_resize(self, event):
        """Calculate the maximum suitable mino size
        and resize the underlying canvases.
        """
        max_width = floor((event.width - 4)
            / (Consts.WIDTH + (len(Rotation)+1) * _config.PICKER_SIZE_MULT))
        max_height = (event.height - 4) // (Consts.TOTAL_HEIGHT)
        mino_size = min(max_width, max_height)
        _config.FONT.config(size=mino_size//2)
        self._field_frame.on_resize(mino_size)
        self._picker_frame.on_resize(
            floor(mino_size*_config.PICKER_SIZE_MULT))
        self._control_frame.on_resize(mino_size)

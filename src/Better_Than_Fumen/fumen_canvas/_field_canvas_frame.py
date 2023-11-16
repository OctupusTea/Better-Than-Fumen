# -*- coding: utf-8 -*-

from copy import copy
from math import floor
from tkinter import ttk, font, Button, Canvas, Frame, Label
from tkinter import N, S, E, W
import tkinter as tk

from py_fumen_py import *
from py_fumen_py.constant import FieldConstants as Consts

from ..config import _keys, _global_config
from ..config import _canvas_config as _config
from ._base_mino_frame import _CanvasMode, _BaseMinoFrame

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
        self._canvas.bind(f'<ButtonPress-{_keys.CANVAS_ERASE_BTN}>',
                          self._on_erase)
        self._canvas.bind(f'<B{_keys.CANVAS_ERASE_BTN}-Motion>',
                          self._on_erase)
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

    def _on_erase(self, event):
        """Erase event handler. Erase mino (draw Mino._)."""
        x, y = self._event_coords(event)
        if self._is_inside_field(x, y):
            if [x, y] in self._placements:
                self._clear_placements()
                _CanvasMode.placement = None
            self._clear_ghosts()
            self._field.fill(x, y, Mino._)
            self._check_lineclear_repaint(x, y)
            self._repaint_ghosts()

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

    def _check_lineclear_repaint(self, x, y, force_repaint=False):
        """Check lineclear (and placements) at the given mino grid coords,
        and repaint accordingly.
        The garbage line(s) are not affected by lineclears.
        """
        if y >= 0:
            lineclear = all([px, y] in self._placements
                            or self._field.at(px, y) is not Mino._
                            for px in range(self._width))
            if force_repaint or lineclear != self._lineclear[y]:
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
            self._check_lineclear_repaint(0, y, True)
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

    def mirror(self):
        if _CanvasMode.placement:
            _CanvasMode.placement.mirror()
        self._field.mirror(mirror_color=True)
        self.repaint()

    def clear(self):
        self._field = Field()
        _CanvasMode.placement = None
        self.repaint()

    def field(self):
        return self._field.copy()

    def replace_field(self, field):
        self._field = field.copy()


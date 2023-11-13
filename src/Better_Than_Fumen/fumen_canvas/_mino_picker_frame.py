# -*- coding: utf-8 -*-

from copy import copy
from math import floor
from tkinter import ttk, font, Button, Canvas, Frame, Label
from tkinter import N, S, E, W
import tkinter as tk

from py_fumen_py import *
from py_fumen_py.action import Action
from py_fumen_py.constant import FieldConstants as Consts

from ..config import _keys
from ..config import _canvas_config as _config
from ._base_mino_frame import _CanvasMode, _BaseMinoFrame

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


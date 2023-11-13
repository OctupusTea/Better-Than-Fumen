# -*- coding: utf-8 -*-

from copy import copy
from math import floor
from tkinter import ttk, font, Button, Canvas, Frame, Label
from tkinter import N, S, E, W
import tkinter as tk

from py_fumen_py import *

from ..config import _keys
from ..config import _canvas_config as _config

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


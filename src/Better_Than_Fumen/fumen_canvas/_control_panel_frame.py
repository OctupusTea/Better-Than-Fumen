# -*- coding: utf-8 -*-

from copy import copy
from math import floor
from tkinter import ttk, font, Button, Canvas, Frame, Label
from tkinter import N, S, E, W
import tkinter as tk

from ..config import _keys
from ..config import _canvas_config as _config
from ._base_mino_frame import _CanvasMode

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


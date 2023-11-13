# -*- coding: utf-8 -*-

from tkinter import ttk, font, Button, Frame, Label
from tkinter import N, S, E, W
import tkinter as tk

from ..config import _keys, _global_config
from ..config import _canvas_config as _config

class _ControlPanelFrame(ttk.Frame):
    """The control panel for the fumen canvas."""
    def __init__(self, parent, unit_size, **kwargs):
        """Keyword arguments:
        parent: the parent of this panel as a tkinter widget.
        unit_size: the displayeing unit size (mino_size of the canvas)
        """
        super().__init__(parent, **kwargs)
        self._unit_size = unit_size
        self._paddings = []

        self._insert_button = Button(
            self, text='Insert', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._insert_button.grid(
            column=0, row=0, columnspan=4, sticky=(N,S,E,W)
        )

        self._copy_button = Button(
            self, text='Copy', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._copy_button.grid(
            column=0, row=1, columnspan=4, sticky=(N,S,E,W)
        )

        self._delete_button = Button(
            self, text='Delete', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._delete_button.grid(
            column=0, row=2, columnspan=4, sticky=(N,S,E,W)
        )

        self._first_button = Button(
            self, text='|<', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._first_button.grid(column=0, row=3, sticky=(N,S,E,W))

        self._prev_button = Button(
            self, text='<<', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._prev_button.grid(column=1, row=3, sticky=(N,S,E,W))

        self._next_button = Button(
            self, text='>>', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._next_button.grid(column=2, row=3, sticky=(N,S,E,W))

        self._last_button = Button(
            self, text='>|', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._last_button.grid(column=3, row=3, sticky=(N,S,E,W))

        self._page_label = Label(
            self, text='1/1', font=_global_config.FONT,
            relief='flat', borderwidth=_config.LINE_WIDTH,
        )
        self._page_label.grid(column=0, row=4, columnspan=4, sticky=(N,S,E,W))

        self._paddings.append(ttk.Label(self, relief='flat'))
        self._paddings[-1].grid(column=0, row=5, columnspan=4,
                                sticky=(N,S,E,W))

        self._shift_left_button = Button(
            self, text='<', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._shift_left_button.grid(column=0, row=6, sticky=(N,S,E,W))

        self._shift_down_button = Button(
            self, text='^', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH, width=2,
        )
        self._shift_down_button.grid(column=1, row=6, sticky=(N,S,E,W))

        self._shift_up_button = Button(
            self, text='v', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH, width=2,
        )
        self._shift_up_button.grid(column=2, row=6, sticky=(N,S,E,W))

        self._shift_right_button = Button(
            self, text='>', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH, width=2,
        )
        self._shift_right_button.grid(column=3, row=6, sticky=(N,S,E,W))

        self._shiftwarp_check = tk.Checkbutton(
            self, text='Shift warp', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH, selectcolor='grey50',
        )
        self._shiftwarp_check.grid(column=0, row=7, columnspan=4,
                                   sticky=(N,S,E,W))

        self._mirror_button = Button(
            self, text='Mirror', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._mirror_button.grid(column=0, row=8, columnspan=2,
                                 sticky=(N,S,E,W))

        self._clear_button = Button(
            self, text='Clear', font=_global_config.FONT,
            borderwidth=_config.LINE_WIDTH,
        )
        self._clear_button.grid(column=2, row=8, columnspan=2,
                                 sticky=(N,S,E,W))

    def update_page_label(self, current, total):
        self._page_label.config(text=f'{current+1}/{total}')

    def bind_commands(self, prev, next_, first, last, delete, copy, insert,
            shift_left, shift_down, shift_up, shift_right, shiftwarp_toggle,
            mirror=None, clear=None):
        self._prev_button.config(command=prev)
        self._next_button.config(command=next_)
        self._first_button.config(command=first)
        self._last_button.config(command=last)
        self._delete_button.config(command=delete)
        self._copy_button.config(command=copy)
        self._insert_button.config(command=insert)
        self._shift_left_button.config(command=shift_left)
        self._shift_down_button.config(command=shift_down)
        self._shift_up_button.config(command=shift_up)
        self._shift_right_button.config(command=shift_right)
        self._shiftwarp_check.config(command=shiftwarp_toggle)
        self._mirror_button.config(command=mirror)
        self._clear_button.config(command=clear)

    def on_resize(self, unit_size):
        self._unit_size = unit_size


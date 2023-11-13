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
from ._base_mino_frame import _CanvasMode
from ._field_canvas_frame import _FieldCanvasFrame
from ._mino_picker_frame import _MinoPickerFrame
from ._control_panel_frame import _ControlPanelFrame

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

        self.bind_all(f'<ButtonPress-{_keys.CANVAS_EXPORT_BTN}>', self._export)

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

    def _export(self, event):
        self._save_current_page()
        print(encode(self._pages))

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

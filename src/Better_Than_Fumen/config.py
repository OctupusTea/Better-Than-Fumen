# -*- coding: utf-8 -*-

from dataclasses import dataclass
from tkinter import font

from py_fumen_py import Mino

@dataclass
class CanvasConfig:
    LINE_WIDTH: int = 2
    MINO_SIZE: int = 32
    PICKER_SIZE_MULT: float = 5/4
    FONT: font = None
    FONT_STYLE: str = 'Fixed'
    TEXT_COLOR = 'gray75'
    FILL: dict = None
    HIGHLIGHT: dict = None
    GRAY_HIGHLIGHT: dict = None
    OUTLINE: dict = None

    def __post_init__(self):
        if self.FILL is None:
            self.FILL = {
                Mino._.value: 'black',
                Mino.I.value: 'cyan',
                Mino.L.value: 'orange',
                Mino.O.value: 'yellow',
                Mino.Z.value: 'red',
                Mino.T.value: 'magenta',
                Mino.J.value: 'blue',
                Mino.S.value: 'green',
                Mino.X.value: 'gray',
            }
        if self.HIGHLIGHT is None:
            self.HIGHLIGHT = {
                'placement': '1',
                'lineclear': '2',
                'normal': '3',
                'ghost': '4',
            }
        if self.GRAY_HIGHLIGHT is None:
            self.GRAY_HIGHLIGHT = {
                'placement': '100',
                'lineclear': '75',
                'normal': '50',
            }
        if self.OUTLINE is None:
            self.OUTLINE = {
                'normal': 'gray25',
                'selected': 'white',
            }

    def mino_fill(self, mino, type_='normal'):
        fill = self.FILL[mino]
        if fill in ['gray' or 'grey']:
            highlight = self.GRAY_HIGHLIGHT[type_]
        elif fill == 'black':
            highlight = ''
        else:
            highlight = self.HIGHLIGHT[type_]
        return ''.join((fill, highlight))


@dataclass
class KeyConfig:
    CANVAS_INVERT_MOD = 'Shift'
    CANVAS_SHIFT_MOD = 'Shift'
    CANVAS_DRAW_BTN = '1'
    CANVAS_EXPORT_BTN = '2'
    CANVAS_ERASE_BTN = '3'
    PICKER_SELECT_BTN = '1'
    PICKER_WHEEL_ENABLED = True
    PICKER_WHEEL_REVERSED = False
    PICKER_WHEEL_MOD = 'Shift'
    FUMEN_PAGEDOWN = 'Next'
    FUMEN_PAGEUP = 'Prior'
    FUMEN_FIRST = 'Home'
    FUMEN_LAST = 'End'

_keys = KeyConfig()
_canvas_config = CanvasConfig()

class ConfigParser:
    @staticmethod
    def parse_config():
        global _keys
        global _canvas_config

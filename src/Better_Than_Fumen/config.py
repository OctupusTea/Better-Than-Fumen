# -*- coding: utf-8 -*-

from dataclasses import dataclass

from py_fumen_py import Mino

@dataclass
class CanvasConfig:
    MINO_SIZE: int = 40
    LINE_WIDTH: int = 2
    PICKER_SIZE: float = 50
    FILL: dict = {
        Mino._: 'black',
        Mino.I: 'cyan',
        Mino.L: 'orange',
        Mino.O: 'yellow',
        Mino.Z: 'red',
        Mino.T: 'magenta',
        Mino.J: 'blue',
        Mino.S: 'green',
    }
    HIGHLIGHT: dict = {
        'placement': '1',
        'lineclear': '2',
        'normal': '3',
        'ghost': '4',
    }
    OUTLINE: dict = {
        'normal': 'gray25',
        'selected': 'white',
    }

@dataclass
class KeyConfig:
    CANVAS_INVERT_MOD = 'Shift'
    CANVAS_DRAW_BTN = '1'

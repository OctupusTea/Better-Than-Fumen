# -*- coding: utf-8 -*-

from enum import *
from tkinter import ttk
from tkinter import *

from .fumen_canvas_frame import FumenCanvasFrame

if __name__ == '__main__':
    root = Tk()
    root.title('Better Than Fumen v0.0.1')

    fumen_canvas = FumenCanvasFrame(root)
    fumen_canvas.pack(fill=BOTH, expand=YES)
    fumen_canvas.focus_set()

    root.mainloop()


from enum import *
from tkinter import ttk
from tkinter import *

from fumenCanvas import FumenCanvas

MINO_SIZE = 40
if __name__ == '__main__':
    root = Tk()
    root.title('Better Than Fumen v0.0.1')

    fumen_canvas = FumenCanvas(root, MINO_SIZE)
    fumen_canvas.grid(column=0, row=0)
    fumen_canvas.pack(fill=BOTH, expand=YES)

    root.mainloop()


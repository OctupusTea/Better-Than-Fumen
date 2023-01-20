from enum import *
from tkinter import ttk
from tkinter import *

from minoField import MinoField
from minoPicker import MinoPicker

MINO_SIZE = 40
if __name__ == '__main__':
    root = Tk()
    root.title('Test Window')
    frame = Frame(padx=5, pady=5, bg='gray25')
    frame.grid()
    main_field = MinoField(frame, mino_size=MINO_SIZE, height=20, width=10)
    main_field.grid(column=2, row=0)
    rise_field = MinoField(frame, mino_size=MINO_SIZE, height=1, width=10)
    rise_field.grid(column=2, row=1)
    selection_field = MinoPicker(frame, mino_size=MINO_SIZE)
    selection_field.grid(column=1, row=0, sticky=(N))

    root.mainloop()


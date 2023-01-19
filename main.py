from enum import *
from tkinter import ttk
from tkinter import *

MINO_SIZE = 40

class Mino:
    class MinoType(Enum):
        PLACEMENT = 1
        LINECLEAR = 2
        NORMAL = 3

    class MinoColor(IntEnum):
        black = 0
        cyan = 1
        orange = 2
        yellow = 3
        red = 4
        magenta = 5
        blue = 6
        green = 7
        gray = 8

    class MinoName(IntEnum):
        _ = 0
        I = 1
        L = 2
        O = 3
        Z = 4
        T = 5
        J = 6
        S = 7
        G = 8

    def __init__(self, name=MinoName._, type=MinoType.NORMAL):
        self.__mino = self.MinoName(name)
        self.__type = self.MinoType(type)

    def type(self):
        return self.__type.value

    def name(self):
        return self.__mino.name

    def value(self):
        return self.__mino.value

    def color(self):
        return self.MinoColor(self.__mino.value).name

    def is_empty(self):
        return self.__mino.value == 0

    def next(self):
        return Mino((self.__mino + 1) % len(self.MinoName), self.__type)

    def prev(self):
        return Mino((self.__mino - 1) % len(self.MinoName), self.__type)

    def lineclear(self):
        self.__type = self.MinoType.LINECLEAR

    def unclear(self):
        self.__type = self.MinoType.NORMAL


class MinoField(Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.__field=[[Mino()for j in range(21)] for i in range(10)]
        self.__mino = Mino()
        self.__drawing_mino = Mino()
        self.bind('<ButtonPress-1>', self.__on_b1)
        self.bind('<B1-Motion>', self.__on_b1)
        self.bind('<ButtonRelease-1>', self.__draw_reset)
        self.bind('<Button-4>', self.__next_mino)
        self.bind('<Button-5>', self.__prev_mino)

    def __on_b1(self, event):
        x = (event.x-1) // MINO_SIZE
        y = (event.y-1) // MINO_SIZE
        if 0 <= x < 10 and 0 <= y < 21:
            if self.__drawing_mino == None:
                self.__drawing_mino = Mino() if self.__mino.value() == self.__field[x][y].value() else self.__mino
            self.__field[x][y] = self.__drawing_mino
            self.__draw_mino(x, y)

    def __draw_reset(self, event):
        self.__drawing_mino = None

    def __draw_mino(self, x, y, mino=None):
        mino = self.__drawing_mino if mino == None else mino
        color = mino.color() if mino.name() in ['_', 'G'] else mino.color() + str(mino.type())
        super().create_rectangle(x*MINO_SIZE, y*MINO_SIZE, (x+1)*MINO_SIZE, (y+1)*MINO_SIZE, fill=color, outline='gray25', width=3)

    def __next_mino(self, event):
        self.__mino = self.__mino.next()

    def __prev_mino(self, event):
        self.__mino = self.__mino.prev()

    def __check_lineclear(self, y):
        return all(mino != 0 for mino in __field[0:-1][y])

if __name__ == '__main__':
    root = Tk()
    root.title('Test Window')
    frame = ttk.Frame(padding=5)
    frame.grid()
    field = MinoField(frame, width=10*MINO_SIZE+1, height=20*MINO_SIZE+1)
    field.grid(column=0, row=0)


    for i in range(10):
        for j in range(20):
            field.create_rectangle(i*MINO_SIZE, j*MINO_SIZE, (i+1)*MINO_SIZE, (j+1)*MINO_SIZE, fill='black', outline='gray25', width=3)

    root.mainloop()


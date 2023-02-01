import math
from tkinter import ttk
from tkinter import *
from tkinter import font

import py_fumen

from mino import *

# Base class for _MinoPicker and _MinoCanvas
class _MinoField(Canvas):
    def __init__(self, parent, mino_size, height, width, selected_mino, line_width=2):
        super().__init__(parent, height=height*mino_size, width=width*mino_size)
        self._height = height
        self._width = width
        self._mino_size = mino_size
        self._selected_mino = selected_mino
        self._line_width = line_width
        # internal mino state
        self._field=[[Mino()for y in range(height)] for x in range(width)]
        # canvas rectangles for later deletion
        self._rects=[[None for y in range(height)] for x in range(width)]
        # initial mino grid painting
        for x in range(width):
            for y in range(height):
                self._draw_mino(x, y)

    # convert event coordinates to mino coordinates
    def _event_coord(self, event):
        x = (event.x-1) // self._mino_size
        y = (event.y-1) // self._mino_size
        return x, y

    # test if mino coordinates are inside the field
    def _is_inside(self, x, y):
        return (0 <= x < self._width and 0 <= y < self._height)

    # draw [mino] on position [x] [y] of the field, with/without selected highlight (for _MinoPicker)
    def _draw_mino(self, x, y, mino=None, selected=False):
        mino = self._field[x][y] if mino is None else mino
        if self._is_inside(x, y):
            outline_color = 'white' if selected else mino.outline_color()
            # if the position is already occupied, delete the previous rectangle
            if self._rects[x][y] is not None:
                self.delete(self._rects[x][y])
            self._rects[x][y] = self.create_rectangle(
                    x*self._mino_size+2, y*self._mino_size+2,
                    (x+1)*self._mino_size, (y+1)*self._mino_size,
                    fill=mino.fill_color(), outline=outline_color, width=self._line_width
            )

    def redraw(self):
        for x in range(self._width):
            for y in range(self._height):
                self._draw_mino(x, y)

    def resize(self, mino_size):
        # re-render only if the size actually changes
        if self._mino_size != mino_size:
            self._mino_size = mino_size
            self.config(height=self._height*mino_size, width=self._width*mino_size)
            self.redraw()

# mino sketch board, for both normal and rising Fumen frames
class _MinoCanvas(_MinoField):
    def __init__(self, parent, mino_size, height, width, selected_mino, placement_tetromino):
        super().__init__(parent, mino_size, height, width, selected_mino)
        self._drawing_mino = None
        self._placement_tetromino = placement_tetromino
        self._placement_coords = []
        self._ghost_coords = []
        self._lineclear = [False for y in range(height)]

        self.bind('<Shift-ButtonPress-1>', self._on_shift_b1)
        self.bind('<Shift-B1-Motion>', self._on_shift_b1)
        self.bind('<ButtonPress-1>', self._on_b1)
        self.bind('<B1-Motion>', self._on_b1)
        self.bind('<ButtonRelease-1>', self._on_b1_release)

    '''
    ## _on_b1
    - clicking on mino x, y
        - if it's placement, reset placement
        - clear ghost and redraw
        - if x, y is the same as the selected mino, set to eraser ('_' mino)
    '''
    def _on_b1(self, event):
        x, y = self._event_coord(event)
        if self._is_inside(x, y):
            if self._field[x][y].is_placement():
                self._clear_placements()
            self._clear_ghosts()
            if self._drawing_mino is None:
                # set to eraser ('_' mino) if the field mino is the same as the selected mino
                if self._field[x][y].value() == self._selected_mino.value():
                    self._drawing_mino = Mino()
                # just draw the selected mino otherwise
                else:
                    self._drawing_mino = Mino.copy(self._selected_mino)

            if self._field[x][y].value() != self._drawing_mino.value():
                self._field[x][y].value(self._drawing_mino.value())
                self._check_lineclear_redraw(x, y)
            self._project_ghosts()
            self._draw_ghosts()

    # reset if the mouse button is released
    def _on_b1_release(self, event):
        self._drawing_mino = None

    # check placement availability, draw placement and ghost
    def _on_shift_b1(self, event):
        x, y = self._event_coord(event)
        if self._is_inside(x, y):
            self._placement_tetromino.mino_value(self._selected_mino.value())
            placement_tests = self._placement_tetromino.placement_tests(x, y)
            if all(self._is_inside(x, y) and self._field[x][y].is_placeable() for x, y in placement_tests):
                self._clear_placements()
                self._placement_coords = placement_tests
                self._project_ghosts()
                self._draw_placements()
                self._draw_ghosts()

    # check for lineclear at row [y] and redraw the line
    def _check_lineclear_redraw(self, x, y):
        lineclear = all(not column[y].is_empty() for column in self._field)
        if lineclear != self._lineclear[y]:
            self._lineclear[y] = lineclear
            for x in range(self._width):
                if lineclear:
                    self._field[x][y].lineclear()
                else:
                    self._field[x][y].unclear()
                self._draw_mino(x, y)
        else:
            self._draw_mino(x, y)

    # the loop iterates down, testing if the ghosts-to-be are all inside and empty
    def _project_ghosts(self):
        projection_dy = 0
        for dy in range (1, self._height):
            # if space available: all of the sub-minos are both inside and empty
            if all(self._is_inside(x, y+dy) and self._field[x][y+dy].is_placeable() for x, y in self._placement_coords):
                projection_dy = dy
            else:
                break
        self._ghost_coords = [(x, y+projection_dy) for x, y in self._placement_coords]

    def _clear_ghosts(self):
        for x, y in self._ghost_coords:
            if self._is_inside(x, y) and self._field[x][y].is_ghost():
                self._field[x][y].reset()
                self._draw_mino(x, y)
        self._ghost_coords.clear()

    def _draw_ghosts(self):
        ghost = Mino(self._placement_tetromino.mino_value(), 4)
        for x, y in self._ghost_coords:
            if self._is_inside(x, y) and self._field[x][y].is_empty():
                self._field[x][y].set_mino(ghost)
                self._draw_mino(x, y)

    def _clear_placements(self):
        for x, y in self._placement_coords:
            if self._is_inside(x, y) and self._field[x][y].is_placement():
                self._field[x][y].reset()
                self._check_lineclear_redraw(x, y)
        self._placement_coords.clear()
        self._clear_ghosts()

    def _draw_placements(self):
        placement = Mino(self._placement_tetromino.mino_value(), 1)
        for x, y in self._placement_coords:
            if self._is_inside(x, y) and self._field[x][y].is_empty():
                self._field[x][y].set_mino(placement)
                self._check_lineclear_redraw(x, y)

    def _shift_placements(self, dx, dy):
        for i, pos in enumerate(self._placement_coords):
            self._placement_coords[i] = (pos[0]+dx, pos[1]+dy)
        for i, pos in enumerate(self._ghost_coords):
            self._ghost_coords[i] = (pos[0]+dx, pos[1]+dy)
        if not all(self._is_inside(x, y) for x, y in self._placement_coords):
            self._clear_placements()
        self._clear_ghosts()
        self._project_ghosts()
        self._draw_ghosts()

    def shift_up(self, amount=1):
        for y in range(self._height-amount):
            for x in range(self._width):
                self._field[x][y] = self._field[x][y+amount]
        for y in range(self._height-amount, self._height):
            for x in range(self._width):
                self._field[x][y] = Mino()
        self.redraw()
        self._shift_placements(0, -amount)

    def shift_down(self, amount=1):
        for y in range(self._height-1, amount-1, -1):
            for x in range(self._width):
                self._field[x][y] = self._field[x][y-amount]
        for y in range(amount):
            for x in range(self._width):
                self._field[x][y] = Mino()
        self.redraw()
        self._shift_placements(0, amount)

    def shift_left(self, amount=1, border_warp=False):
        shifted_columns = self._field[:amount] if border_warp else [[Mino() for y in range(self._height)] for x in range(amount)]
        self._field[:-amount] = self._field[amount:]
        self._field[-amount:] = shifted_columns
        self.redraw()
        self._shift_placements(-amount, 0)

    def shift_right(self, amount=1, border_warp=False):
        shifted_columns = self._field[-amount:] if border_warp else [[Mino() for y in range(self._height)] for x in range(amount)]
        self._field[amount:] = self._field[:-amount]
        self._field[:amount] = shifted_columns
        self.redraw()
        self._shift_placements(amount, 0)

    def field_string(self):
        return ''.join(self._field[x][y].name() for y in range(self._height) for x in range(self._width))

# mino picker
class _MinoPicker(_MinoField):
    def __init__(self, parent, mino_size, selected_mino):
        super().__init__(parent, mino_size, Mino.count(), 1, selected_mino)
        self._previous_mino = Mino.copy(self._selected_mino)

        # pre-draw the mino color on the picker
        for y in range(Mino.count()):
            self._field[0][y] = Mino(y)
            self._draw_mino(0, y)

        self.bind('<ButtonPress-1>', self._on_b1)

    def _on_b1(self, event):
        x, y = self._event_coord(event)
        if self._is_inside(x, y):
            self._selected_mino.value(y)
            self.update_mino()

    # un-highlight the previously selected mino and highlight the current one
    def update_mino(self):
        self._draw_mino(0, self._previous_mino.value(), self._previous_mino)
        self._previous_mino.set_mino(self._selected_mino)
        self._draw_mino(0, self._selected_mino.value(), self._selected_mino, True)

# main Fumen canvas class
class FumenCanvas(Frame):
    # shared values across all instances
    _mino_size = 40
    _canvas_width = 10
    _canvas_height = 20

    def __init__(self, parent, mino_size):
        super().__init__(parent)
        self._selected_mino = Mino()
        self._placement_tetromino = PlacementTetromino(mino_value=self._selected_mino.value())
        self._pages = [None]
        self._current_page = 0

        self._main_frame = ttk.Frame(self, padding=2)
        self._main_frame.grid(column=1, row=0, sticky=(S,W))
        self._main_canvas = _MinoCanvas(
                self._main_frame,
                self._mino_size, self._canvas_height, self._canvas_width,
                self._selected_mino, self._placement_tetromino
        )
        self._main_canvas.grid()

        self._rise_frame = ttk.Frame(self, padding=2)
        self._rise_frame.grid(column=1, row=1, sticky=(N,W))
        self._rise_canvas = _MinoCanvas(
                self._rise_frame,
                self._mino_size, 1, self._canvas_width,
                self._selected_mino, self._placement_tetromino
        )
        self._rise_canvas.grid()

        self._pick_frame = ttk.Frame(self, padding=2)
        self._pick_frame.grid(column=0, row=0, sticky=(S,E))
        self._pick_canvas = _MinoPicker(
                self._pick_frame,
                self._mino_size*1.5,
                self._selected_mino
        )
        self._pick_canvas.grid()
        self._pick_canvas.update_mino()

        self._rotation_frame = ttk.Frame(self, padding=2)
        self._rotation_frame.grid(column=0, row=1, sticky=(E,W,S,N))
        self._rotation_label = ttk.Label(
                self._rotation_frame,
                textvariable=self._placement_tetromino.rotation_strvar(),
                font=("TkDefaultFont", self._mino_size//2, NORMAL)
        )
        self._rotation_label.pack()

        self.bind_all('<Button-3>', self.to_fumen)
        self.bind_all('<Shift-Button-4>', self._on_shift_mousewheel)
        self.bind_all('<Shift-Button-5>', self._on_shift_mousewheel)
        self.bind_all('<Shift-MouseWheel>', self._on_shift_mousewheel)
        self.bind_all('<Button-4>', self._on_mousewheel)
        self.bind_all('<Button-5>', self._on_mousewheel)
        self.bind_all('<MouseWheel>', self._on_mousewheel)

        self.bind('<Configure>', self._on_resize)

        self.bind('<Shift-Up>', self._on_shift_up)
        self.bind('<Shift-Down>', self._on_shift_down)
        self.bind('<Shift-Left>', self._on_shift_left)
        self.bind('<Shift-Right>', self._on_shift_right)

    def _on_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            self._prev_mino()
        else:
            self._next_mino()
        self._pick_canvas.update_mino()
        self._placement_tetromino.rotate(0)

    def _prev_mino(self):
        self._selected_mino.to_prev()

    def _next_mino(self):
        self._selected_mino.to_next()

    def _on_shift_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            self._prev_rotation()
        else:
            self._next_rotation()
        self._pick_canvas.update_mino()

    def _prev_rotation(self):
        self._placement_tetromino.to_prev_rotation()

    def _next_rotation(self):
        self._placement_tetromino.to_next_rotation()

    def _on_resize(self, event):
        max_width = math.floor((event.width - 12) / (self._canvas_width + 1.5))
        max_height = (event.height - 12) // (self._canvas_height + 1)
        self._mino_size = min(max_width, max_height)
        self._main_canvas.resize(self._mino_size)
        self._rise_canvas.resize(self._mino_size)
        self._pick_canvas.resize(self._mino_size*1.5)
        self._rotation_label.config(font=("TkDefaultFont", self._mino_size//2, NORMAL))

    def _on_shift_up(self, event):
        self._main_canvas.shift_up()

    def _on_shift_down(self, event):
        self._main_canvas.shift_down()

    def _on_shift_left(self, event):
        self._main_canvas.shift_left()

    def _on_shift_right(self, event):
        self._main_canvas.shift_right()

    def to_fumen(self, event):
        self._pages[self._current_page] = py_fumen.page.Page(
            field=py_fumen.field.create_inner_field(
                py_fumen.field.Field.create(
                    self._main_canvas.field_string(),
                    self._rise_canvas.field_string()
                )
            ),comment='Test'
        )
        print(py_fumen.encode(self._pages))


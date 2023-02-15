import math
from tkinter import ttk, font, Frame, Canvas
from tkinter import E, W, S, N

import py_fumen

from common import MinoType, MinoColor, MinoName, Pos
from mino import Mino, PlacementTetromino

# Base class for _MinoPicker and _MinoCanvas
class _MinoField(Canvas):
    def __init__(self, parent, mino_size, height, width, selected_mino, line_width=2):
        super().__init__(parent, height=height*mino_size, width=width*mino_size)
        self._height = height
        self._width = width
        self._mino_size = mino_size
        self._selected_mino = selected_mino
        self._line_width = line_width
        # initialize field minos
        self._field=[[Mino() for y in range(height)] for x in range(width)]
        # initialize canvas rectangles
        self._rects=[[
                self.create_rectangle(
                    x*self._mino_size+2, y*self._mino_size+2,
                    (x+1)*self._mino_size, (y+1)*self._mino_size,
                    fill='black',
                    outline='gray25', width=self._line_width
                ) for y in range(height)
            ] for x in range(width)
        ]

    # convert event coordinates to mino coordinates
    def _event_coords(self, event):
        return math.floor((event.x-1)//self._mino_size), math.floor((event.y-1)//self._mino_size)

    def _event_pos(self, event):
        return Pos(*self._event_coords(event))

    # test if mino coordinates are inside the field
    def _is_inside(self, x, y):
        return 0 <= x < self._width and 0 <= y < self._height

    # Draw mino on position x, y of the field,
    # with or without selected highlight (for _MinoPicker)
    def _paint_mino(self, x, y, mino=None, selected=False):
        if self._is_inside(x, y) and self._field[x][y] is not None:
            mino = self._field[x][y] if mino is None else mino
            outline_color = 'white' if selected else mino.outline_color()
            # if the position is already occupied, delete the previous rectangle
            if self._rects[x][y] is None:
                self.delete(self._rects[x][y])
            self.itemconfigure(
                self._rects[x][y],
                fill=mino.fill_color(),
                outline=outline_color,
            )

    def repaint(self):
        for x in range(self._width):
            for y in range(self._height):
                self._paint_mino(x, y)

    def resize(self, mino_size):
        # repaint only if the size actually changes
        if self._mino_size != mino_size:
            self._mino_size = mino_size
            self.config(height=self._height*mino_size, width=self._width*mino_size)
            for x in range(self._width):
                for y in range(self._height):
                    self.coords(
                        self._rects[x][y],
                        x*self._mino_size+2, y*self._mino_size+2,
                        (x+1)*self._mino_size, (y+1)*self._mino_size,
                    )
            return True
        else:
            return False

# mino sketch board, for both normal and rising Fumen frames
class _MinoCanvas(_MinoField):
    def __init__(
            self, parent, mino_size, height, width,
            selected_mino, placement_tetromino):
        super().__init__(parent, mino_size, height, width, selected_mino)
        self._drawing_mino = None
        self._placement_tetromino = placement_tetromino
        self._ghost_coords = []
        self._lineclear = [False for y in range(height)]

        self.bind('<Shift-ButtonPress-1>', self._on_shift_b1)
        self.bind('<Shift-B1-Motion>', self._on_shift_b1)
        self.bind('<ButtonPress-1>', self._on_b1)
        self.bind('<B1-Motion>', self._on_b1)
        self.bind('<ButtonRelease-1>', self._on_b1_release)

    def _on_b1(self, event):
        x, y = self._event_coords(event)
        if self._placement_tetromino.direct_place and self._selected_mino.is_colored():
            self._draw_placement(x, y)
        else:
            self._draw_mino(x, y)

    # reset if the mouse button is released
    def _on_b1_release(self, event):
        self._drawing_mino = None

    def _on_shift_b1(self, event):
        x, y = self._event_coords(event)
        if self._placement_tetromino.direct_place or not self._selected_mino.is_colored():
            self._draw_mino(x, y)
        else:
            self._draw_placement(x, y)

    """
    ## _on_b1
    - clicking on mino x, y
        - if it's placement, reset placement
        - clear ghost and repaint
        - if field[x][y] is the same as the selected mino,
            set to eraser ('_' mino)
    """
    def _draw_mino(self, x, y):
        if self._is_inside(x, y):
            if self._field[x][y].is_placement():
                self._clear_placements()
            self._clear_ghosts()
            if self._drawing_mino is None:
                self._drawing_mino = Mino()
                # keep as eraser ('_' mino) if the starting field mino
                # is the same as the selected one;
                # otherwise, draw the selected mino
                if self._field[x][y].name is not self._selected_mino.name:
                    self._drawing_mino.set_mino(self._selected_mino)

            if self._field[x][y].name is not self._drawing_mino.name:
                self._field[x][y].name = self._drawing_mino.name
                self._check_lineclear_repaint(x, y)
            self._repaint_ghosts() 

    # check placement availability, draw placement and ghost
    def _draw_placement(self, x, y):
        if self._is_inside(x, y):
            self._placement_tetromino.mino.name = self._selected_mino.name
            self._placement_tetromino.pos = Pos(x, y)
            self._placement_tetromino.gen_coords()
            if all(self._is_inside(px, py)
                    and self._field[px][py].is_placeable()
                        for px, py in self._placement_tetromino.coords):
                self._clear_placements()
                self._placement_tetromino.place()
                self._paint_placements()
                self._repaint_ghosts()

    # check for lineclear at row [y] and repaint the line
    def _check_lineclear_repaint(self, x, y):
        lineclear = all(not column[y].is_placeable() for column in self._field)
        if lineclear != self._lineclear[y]:
            self._lineclear[y] = lineclear
            for x in range(self._width):
                if lineclear:
                    self._field[x][y].lineclear()
                else:
                    self._field[x][y].unclear()
                self._paint_mino(x, y)
        else:
            self._paint_mino(x, y)

    def _clear_ghosts(self):
        for x, y in self._ghost_coords:
            if self._is_inside(x, y) and self._field[x][y].is_ghost():
                self._field[x][y].reset()
                self._paint_mino(x, y)
        self._ghost_coords.clear()

    def _repaint_ghosts(self):
        self._clear_ghosts()
        projection_dy = 0
        # the loop iterates down, testing if the ghosts-to-be are all inside and empty
        for dy in range (1, self._height):
            # if space available: all of the sub-minos are both inside and empty
            if all(self._is_inside(x, y+dy)
                    and self._field[x][y+dy].is_placeable()
                        for x, y in self._placement_tetromino.placed_coords):
                projection_dy = dy
            else:
                break
        self._ghost_coords = [Pos(x, y+projection_dy)
                for x, y in self._placement_tetromino.placed_coords]

        ghost = Mino(self._placement_tetromino.placed_mino.name, MinoType.GHOST)
        for x, y in self._ghost_coords:
            if self._is_inside(x, y) and self._field[x][y].is_empty():
                self._field[x][y].set_mino(ghost)
                self._paint_mino(x, y)

    def _clear_placements(self):
        for x, y in self._placement_tetromino.placed_coords:
            if self._is_inside(x, y) and self._field[x][y].is_placement():
                self._field[x][y].reset()
                self._check_lineclear_repaint(x, y)
        self._placement_tetromino.clear()
        self._clear_ghosts()

    def _paint_placements(self):
        placement = Mino(self._placement_tetromino.mino.name, MinoType.PLACEMENT)
        for x, y in self._placement_tetromino.coords:
            if self._is_inside(x, y) and self._field[x][y].is_placeable():
                self._field[x][y].set_mino(placement)
                self._check_lineclear_repaint(x, y)

    def _shift_placements(self, dx, dy):
        dpos = Pos(dx, dy)
        for pos in self._placement_tetromino.placed_coords:
            pos += dpos
        for pos in self._ghost_coords:
            pos += dpos
        if not all(self._is_inside(x, y) for x, y
                in self._placement_tetromino.placed_coords):
            self._clear_placements()
        self._repaint_ghosts()

    def shift_up(self, amount=1):
        for y in range(self._height-amount):
            for x in range(self._width):
                self._field[x][y] = self._field[x][y+amount]
        for y in range(self._height-amount, self._height):
            for x in range(self._width):
                self._field[x][y] = Mino()
        self.repaint()
        self._shift_placements(0, -amount)

    def shift_down(self, amount=1):
        for y in range(self._height-1, amount-1, -1):
            for x in range(self._width):
                self._field[x][y] = self._field[x][y-amount]
        for y in range(amount):
            for x in range(self._width):
                self._field[x][y] = Mino()
        self.repaint()
        self._shift_placements(0, amount)

    def shift_left(self, amount=1, border_warp=False):
        shifted_columns = self._field[:amount]\
            if border_warp else [[
                Mino() for y in range(self._height)] for x in range(amount)
            ]
        self._field[:-amount] = self._field[amount:]
        self._field[-amount:] = shifted_columns
        self.repaint()
        self._shift_placements(-amount, 0)

    def shift_right(self, amount=1, border_warp=False):
        shifted_columns = self._field[-amount:]\
            if border_warp else [[
                Mino() for y in range(self._height)] for x in range(amount)
            ]
        self._field[amount:] = self._field[:-amount]
        self._field[:amount] = shifted_columns
        self.repaint()
        self._shift_placements(amount, 0)

    def field_string(self):
        return ''.join(self._field[x][y].fumen_name()
                for y in range(self._height) for x in range(self._width))

# mino picker
class _MinoPicker(_MinoField):
    def __init__(self, parent, mino_size, selected_mino, placement_tetromino):
        super().__init__(parent, mino_size, Mino.count(), 5, selected_mino)
        self._placement_tetromino = placement_tetromino
        self._previous_selection = Pos(4, 0)
        self._texts = [[None for y in range(self._height)] for x in range(self._width)]

        # draw the mino color on the picker
        for y in range(self._height):
            for x in range(self._width):
                self._field[x][y] = Mino(MinoName(y))
                self._paint_mino(x, y)
                if x < self._width - 1:
                    if self._field[x][y].is_colored():
                        self._texts[x][y] = self.create_text(
                            ((x+0.5)*self._mino_size, (y+0.5)*self._mino_size),
                            fill='gray25',
                            text=PlacementTetromino.ROTATIONS[x],
                            font=(
                                "TkDefaultFont",
                                math.floor(self._mino_size//2),
                                font.NORMAL,
                            ),
                        )
                    else:
                        self._field[x][y] = None
                        self.delete(self._rects[x][y])

        self.bind('<ButtonPress-1>', self._on_b1)

    def _on_b1(self, event):
        x, y = self._event_coords(event)
        if self._is_inside(x, y):
            self._placement_tetromino.rotate(x)
            self._selected_mino.name = MinoName(y)
            self._placement_tetromino.direct_place = (
                x < self._width - 1 and
                self._selected_mino.is_colored()
            )
            self.update_mino()

    # un-highlight the previously selected mino and highlight the current one
    def update_mino(self):
        self._paint_mino(*self._previous_selection)
        self._paint_mino(4, self._previous_selection.y)
        self._previous_selection = Pos(
            self._placement_tetromino.rotation if self._selected_mino.is_colored()\
                else 4,
            self._selected_mino.name.value
        )
        self._paint_mino(*self._previous_selection, selected=True)
        if not self._placement_tetromino.direct_place:
            self._paint_mino(4, self._previous_selection.y, selected=True)

    def resize(self, mino_size):
        if super().resize(mino_size):
            for x in range(0, self._width-1):
                for y in range(self._height):
                    if self._field[x][y] is not None and self._field[x][y].is_colored():
                        self.itemconfigure(
                                self._texts[x][y],
                                font=(
                                    "TkDefaultFont",
                                    math.floor(self._mino_size//2),
                                    font.NORMAL,
                                ),
                        )
                        self.tag_raise(self._texts[x][y], self._rects[x][y])
                        self.coords(
                                self._texts[x][y],
                                (x+0.5)*self._mino_size,
                                (y+0.5)*self._mino_size,
                        )

# main Fumen canvas class
class FumenCanvas(ttk.Frame):
    # shared values across all instances
    _mino_size = 40
    _canvas_width = 10
    _canvas_height = 20
    _pick_size_mult = 10/9

    def __init__(self, parent, mino_size):
        super().__init__(parent)
        self._selected_mino = Mino()
        self._placement_tetromino = PlacementTetromino(mino=self._selected_mino)
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
                self._mino_size*self._pick_size_mult,
                self._selected_mino, self._placement_tetromino
        )
        self._pick_canvas.grid()
        self._pick_canvas.update_mino()

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
        max_width = math.floor((event.width - 12)
            / (self._canvas_width + 5 * self._pick_size_mult))
        max_height = (event.height - 12) // (self._canvas_height + 1)
        self._mino_size = min(max_width, max_height)
        self._main_canvas.resize(self._mino_size)
        self._rise_canvas.resize(self._mino_size)
        self._pick_canvas.resize(self._mino_size*self._pick_size_mult)

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
            ),
            operation=py_fumen.field.Operation(
                *self._placement_tetromino.to_fumen_operation_args()
            ) if self._placement_tetromino.placed else None,
            comment='Test'
        )
        print(py_fumen.encode(self._pages))


from abc import ABC, abstractmethod
from board_gui import draw_board, draw_board_full
import random, time
from perf_bot import Position, best_move, WIDTH, HEIGHT

SOLVER_MIN_STONES = 10   # testing only: below this many stones, play randomly

def board_to_position(board, my_symbol):
    rows = board.rows
    if len(rows) != HEIGHT or len(rows[0]) != WIDTH:
        raise ValueError(f"solver supports a {WIDTH}x{HEIGHT} board")
    current = mask = moves = 0
    for r, row in enumerate(rows):
        height = HEIGHT - 1 - r          # 0 = bottom row
        for col, cell in enumerate(row):
            if cell == ' ':
                continue
            bit = 1 << (col * (HEIGHT + 1) + height)
            mask |= bit
            moves += 1
            if cell == my_symbol:
                current |= bit
    pos = Position()
    pos.current, pos.mask, pos.moves = current, mask, moves
    return pos



class AbstractPlayer(ABC):
    def __init__(self, symbol, name):
        self.name = name
        self.symbol = symbol

    @abstractmethod
    def move(self, **kwargs):
        """Return an integer representing the column where the player intends to play a piece."""


class ConsolePlayer(AbstractPlayer):
    def move(self, **kwargs):
        """Get which column to play in from the user via text console"""
        while True:
            raw_input = input('Enter which column to play in: ')
            try:
                return int(raw_input)
            except ValueError:
                print(f'"{raw_input}" is not a number!')

class CPUPlayer(AbstractPlayer):
    def move(self, **kwargs):
        board = kwargs['board']
        pos = board_to_position(board, self.symbol)

        if pos.moves < SOLVER_MIN_STONES:
            valid = [c for c in range(board.num_cols) if board.rows[0][c] == ' ']
            return random.choice(valid)

        start = time.time()
        col, score = best_move(pos)
        print(f"CPU: column {col}, score {score}, {time.time() - start:.1f}s")
        return col

#class CPUPlayer(AbstractPlayer):
#    def move(self, **kwargs):
#        """Select a random available column."""
#        board = kwargs['board']
#
#        valid_columns = []
#
#        for col in range(board.num_cols):
#            if board.rows[0][col] == ' ':
#                valid_columns.append(col)
#
#        return random.choice(valid_columns)

class MatplotlibPlayer(AbstractPlayer):
    def __init__(self, symbol, name, fig, ax, color_map):
        super().__init__(symbol, name)
        self.fig = fig
        self.ax = ax
        self.color_map = color_map

    def move(self, **kwargs):
        board = kwargs['board']

        draw_board_full(self.ax, board, self.color_map)
        self.ax.set_title(f"{self.name}'s turn — click a column to play")
        self.fig.canvas.draw_idle()

        clicked_points = self.fig.ginput(1)  # blocks until one click happens
        x_clicked, y_clicked = clicked_points[0]
        col = round(x_clicked)
        return col


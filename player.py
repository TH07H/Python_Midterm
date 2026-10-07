from abc import ABC, abstractmethod
from board_gui import draw_board, draw_board_full
import random

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
        """Select a random available column."""
        board = kwargs['board']

        valid_columns = []

        for col in range(board.num_cols):
            if board.rows[0][col] == ' ':
                valid_columns.append(col)

        return random.choice(valid_columns)

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


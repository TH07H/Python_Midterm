# Used to indicate empty spaces in the board
_EMPTY = ' '


class InvalidMoveError(ValueError):
    pass


class ConnectFourBoard:

    """Represents a Connect 4 board.

    Handles board state and checks moves for validity.
    """

    def __init__(self, num_rows, num_cols):
        """Initialize a new board"""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.clear()

    def clear(self):
        """Replace all pieces with empty spaces."""
        self.rows = list()
        for row in range(self.num_rows):
            self.rows.append([_EMPTY for col in range(self.num_cols)])

    def display(self):
        """Display the current board state"""
        for row in range(self.num_rows):
            print(f'\t|{"|".join(self.rows[row])}|')
        print('\t ' + ' '.join([str(col) for col in range(self.num_cols)]))

    def check_winner(self):
        for col in reversed(range(self.num_cols)):
            for row in reversed(range(self.num_rows)):
                if not self.rows[row][col] is _EMPTY:
                    symbol = self.rows[row][col]
                    if row > 2:
                        if self.rows[row-1][col] is symbol:
                            if self.rows[row-2][col] is symbol:
                                if self.rows[row-3][col] is symbol:
                                    return True
                    if col < (self.num_cols-3):
                        if self.rows[row][col+1] is symbol:
                            if self.rows[row][col+2] is symbol:
                                if self.rows[row][col+3] is symbol:
                                    return True
                    if col < (self.num_cols-3) and (row > 2):
                        if self.rows[row-1][col+1] is symbol:
                            if self.rows[row-2][col+2] is symbol:
                                if self.rows[row-3][col+3] is symbol:
                                    return True
                    if col < (self.num_cols-3) and row < self.num_rows-3:
                        if self.rows[row+1][col+1] is symbol:
                            if self.rows[row+2][col+2] is symbol:
                                if self.rows[row+3][col+3] is symbol:
                                    return True
        return False

    def is_full(self):
        """Check whether the board is full."""
        for col in reversed(range(self.num_cols)):
            if self.rows[0][col] is _EMPTY:
                return False
        return True

    def add_piece(self, col, symbol):
        """Add a piece to the specified column.

        Returns the row it landed in.
        """
        if not (0 <= col <= self.num_cols - 1):
            raise InvalidMoveError(
                "That isn't a column silly! Play a move on the board!"
            )
        for row in reversed(range(self.num_rows)):
            if self.rows[row][col] is _EMPTY:
                self.rows[row][col] = symbol
                return row
        else:
            raise InvalidMoveError("That column is full!")

    def get_landing_row(self, col):
        """Return the row a piece would land in for this column.

        Returns None if the column is invalid or full.
        """
        if not (0 <= col <= self.num_cols - 1):
            return None
        for row in reversed(range(self.num_rows)):
            if self.rows[row][col] is _EMPTY:
                return row
        return None

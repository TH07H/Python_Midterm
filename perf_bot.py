import json


ROWS = 6
COLS = 7


with open("branches.json", "r") as file:
    branches = json.load(file)

with open("steady_states.json", "r") as file:
    steady_states = json.load(file)


def board_from_position(position):
    """Create a WeakC4 board from a move sequence."""
    board = [[0] * COLS for _ in range(ROWS)]
    heights = [0] * COLS

    for ply, character in enumerate(position):
        col = int(character) - 1
        player = (ply % 2) + 1

        board[heights[col]][col] = player
        heights[col] += 1

    return board


def convert_board(board, player_symbol):
    """Convert the project board to WeakC4's board format."""
    weak_board = [[0] * COLS for _ in range(ROWS)]

    for y in range(ROWS):
        for x in range(COLS):
            symbol = board.rows[ROWS - 1 - y][x]

            if symbol == ' ':
                weak_board[y][x] = 0
            elif symbol == player_symbol:
                weak_board[y][x] = 1
            else:
                weak_board[y][x] = 2

    return weak_board


def col_height(board, col):
    """Return the height of a column."""
    for row in range(ROWS):
        if board[row][col] == 0:
            return row

    return ROWS


def makes_four(board, col, row, player):
    """Check whether a move creates four in a row."""
    for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
        count = 1

        for sign in (1, -1):
            x = col + sign * dx
            y = row + sign * dy

            while (
                0 <= x < COLS
                and 0 <= y < ROWS
                and board[y][x] == player
            ):
                count += 1
                x += sign * dx
                y += sign * dy

        if count >= 4:
            return True

    return False


def query_steady_state(board, diagram):
    """Find Red's move using a WeakC4 steady-state diagram."""

    heights = [col_height(board, x) for x in range(COLS)]

    def wins(x, player):
        y = heights[x]

        if y >= ROWS:
            return False

        board[y][x] = player
        won = makes_four(board, x, y, player)
        board[y][x] = 0

        return won

    # First check immediate winning moves.
    # WeakC4 checks Red first, then Yellow.
    for player in (1, 2):
        for x in range(COLS):
            if wins(x, player):
                return x + 1

    def playable(level_char):
        found = []

        for x in range(COLS):
            y = heights[x]

            if y >= ROWS:
                continue

            diagram_row = ROWS - 1 - y

            if diagram[diagram_row][x] == level_char:
                found.append(x + 1)

        return found

    # Check the levels in order.
    for level_char in "0123456789":
        valid = playable(level_char)

        if len(valid) == 1:
            return valid[0]

    return None


def find_tactical_move(board, symbol):
    """Win immediately or block the opponent's immediate win."""

    opponent = None
    for row in board.rows:
        for piece in row:
            if piece != ' ' and piece != symbol:
                opponent = piece
                break
        if opponent is not None:
            break

    if opponent is None:
        return None

    weak_board = convert_board(board, symbol)
    heights = [col_height(weak_board, col) for col in range(COLS)]

    def can_win(col, player):
        row = heights[col]

        if row >= ROWS:
            return False

        weak_board[row][col] = player
        won = makes_four(weak_board, col, row, player)
        weak_board[row][col] = 0

        return won

    for col in range(COLS):
        if can_win(col, 1):
            return col

    for col in range(COLS):
        if can_win(col, 2):
            return col

    return None


def find_best_move(board, symbol, position):
    """Return the WeakC4 move as a zero-based column."""

    tactical_move = find_tactical_move(board, symbol)

    if tactical_move is not None:
        return tactical_move

    mirrored_position = "".join(
        str(8 - int(ch)) for ch in position
    )

    # Check whether the current position has a direct move
    # or a steady-state diagram.
    for candidate, mirrored in (
        (position, False),
        (mirrored_position, True)
    ):
        if candidate in branches:
            move = branches[candidate]

            # String values represent direct moves.
            if isinstance(move, str):
                move = int(move)

                if mirrored:
                    move = 8 - move

                return move - 1

            # Integer values identify steady-state diagrams.
            weak_board = board_from_position(candidate)
            diagram = steady_states[move]

            best_move = query_steady_state(
                weak_board, diagram
            )

            if best_move is None:
                raise ValueError(
                    f"WeakC4 could not find a move for "
                    f"position {position!r}."
                )

            if mirrored:
                best_move = 8 - best_move

            return best_move - 1

    # No exact branch: use the longest prefix (either orientation)
    # that points to a steady-state diagram.
    best = None
    for candidate, mirrored in (
        (position, False),
        (mirrored_position, True)
    ):
        for end in range(len(candidate), -1, -1):
            if isinstance(branches.get(candidate[:end]), int):
                if best is None or end > best[0]:
                    best = (end, candidate, mirrored)
                break

    if best is not None:
        end, candidate, mirrored = best
        diagram = steady_states[branches[candidate[:end]]]
        best_move = query_steady_state(
            board_from_position(candidate), diagram
        )

        if best_move is not None:
            if mirrored:
                best_move = 8 - best_move

            return best_move - 1

    # The strategy has no answer here, so play the most central
    # open column instead of crashing or picking a full column.
    weak_board = board_from_position(position)
    for col in (3, 2, 4, 1, 5, 0, 6):
        if col_height(weak_board, col) < ROWS:
            return col

    raise ValueError(f"No legal move for position {position!r}.")

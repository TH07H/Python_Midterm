"""Tiny independent Connect 4 solver used as ground truth in the tests.

Bitboard layout: column c uses bits c*7 .. c*7+5 (bit 6 of each column is a
sentinel). Values are from the point of view of the side to move:
1 = forced win, 0 = draw, -1 = forced loss.
"""

import sys

sys.setrecursionlimit(10000)

ROWS = 6
COLS = 7
H = ROWS + 1
ORDER = (3, 2, 4, 1, 5, 0, 6)

BOTTOM = sum(1 << (c * H) for c in range(COLS))
BOARD = sum(((1 << ROWS) - 1) << (c * H) for c in range(COLS))


def is_win(pos):
    for shift in (1, H, H - 1, H + 1):
        m = pos & (pos >> shift)
        if m & (m >> (2 * shift)):
            return True
    return False


def playable(mask):
    return (mask + BOTTOM) & BOARD


def column_move(possible, col):
    return possible & (((1 << ROWS) - 1) << (col * H))


class Solver:
    def __init__(self):
        self.table = {}

    def solve(self, pos, mask, nb):
        """Value for the side to move. pos = stones of the side to move."""
        key = pos + mask
        cached = self.table.get(key)
        if cached is not None:
            return cached

        possible = playable(mask)
        moves = [column_move(possible, c) for c in ORDER]
        moves = [m for m in moves if m]

        if nb == ROWS * COLS:
            return 0

        for m in moves:
            if is_win(pos | m):
                self.table[key] = 1
                return 1

        # Opponent's immediate wins must be blocked.
        opp = pos ^ mask
        threats = [m for m in moves if is_win(opp | m)]
        if len(threats) > 1:
            self.table[key] = -1
            return -1
        if threats:
            moves = threats

        best = -1
        for m in moves:
            v = -self.solve(opp, mask | m, nb + 1)
            if v > best:
                best = v
                if best == 1:
                    break

        self.table[key] = best
        return best


def state_from_position(position):
    """Replay a move string. Returns (pos_of_side_to_move, mask, nb)."""
    heights = [0] * COLS
    mask = 0
    stones = [0, 0]
    for ply, ch in enumerate(position):
        col = int(ch) - 1
        bit = 1 << (col * H + heights[col])
        heights[col] += 1
        stones[ply % 2] |= bit
        mask |= bit
    nb = len(position)
    return stones[nb % 2], mask, nb


def value_for_first_player_after(position, solver=None):
    """Theoretical result for player 1 of the position (any side to move)."""
    solver = solver or Solver()
    pos, mask, nb = state_from_position(position)
    v = solver.solve(pos, mask, nb)
    return v if nb % 2 == 0 else -v

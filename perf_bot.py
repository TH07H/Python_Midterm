"""Connect 4 solver, stage 1: bitboards + negamax with alpha-beta pruning.

Board layout: 7 columns, 6 playable rows, plus 1 sentinel row on top of each
column (so 7 bits per column, 49 bits total). Bit index = col * 7 + row,
with row 0 at the bottom.

    .  .  .  .  .  .  .     <- sentinel row (always empty)
    5 12 19 26 33 40 47
    4 11 18 25 32 39 46
    3 10 17 24 31 38 45
    2  9 16 23 30 37 44
    1  8 15 22 29 36 43
    0  7 14 21 28 35 42
"""

WIDTH = 7
HEIGHT = 6
H1 = HEIGHT + 1  # bits per column, including the sentinel


def bottom_mask(col):
    """A single bit set at the bottom cell of a column."""
    return 1 << (col * H1)


def top_mask(col):
    """A single bit set at the top playable cell of a column."""
    return 1 << (HEIGHT - 1 + col * H1)


def column_mask(col):
    """All 6 playable cells of a column."""
    return ((1 << HEIGHT) - 1) << (col * H1)


# Every playable cell on the board, and the bottom cell of every column.
BOARD_MASK = 0
BOTTOM_ALL = 0
for _c in range(WIDTH):
    BOARD_MASK |= column_mask(_c)
    BOTTOM_ALL |= bottom_mask(_c)

# Number of set bits in an integer.
popcount = int.bit_count if hasattr(int, "bit_count") else (lambda x: bin(x).count("1"))


def winning_cells(pos, mask):
    """Empty cells where the owner of bitboard `pos` would complete four.

    For each direction (shift s), a cell x completes a line if the other three
    cells of some window of four containing x are all stones. The four windows
    are: x-3s..x-s, x-2s..x+s, x-s..x+2s, x+s..x+3s.
    """
    # vertical: three stones directly below
    r = (pos << 1) & (pos << 2) & (pos << 3)
    # horizontal (s = 7) and both diagonals (s = 6 and s = 8)
    for s in (H1, HEIGHT, HEIGHT + 2):
        p = (pos << s) & (pos << 2 * s)
        r |= p & (pos << 3 * s)
        r |= p & (pos >> s)
        p = (pos >> s) & (pos >> 2 * s)
        r |= p & (pos << s)
        r |= p & (pos >> 3 * s)
    # keep only cells that are on the board and still empty
    return r & (BOARD_MASK ^ mask)


def alignment(pos):
    """True if the bitboard `pos` contains four in a row in any direction."""
    # horizontal (neighbors are H1 bits apart)
    m = pos & (pos >> H1)
    if m & (m >> (2 * H1)):
        return True
    # diagonal \ (neighbors are HEIGHT bits apart)
    m = pos & (pos >> HEIGHT)
    if m & (m >> (2 * HEIGHT)):
        return True
    # diagonal / (neighbors are HEIGHT + 2 bits apart)
    m = pos & (pos >> (HEIGHT + 2))
    if m & (m >> (2 * (HEIGHT + 2))):
        return True
    # vertical (neighbors are 1 bit apart)
    m = pos & (pos >> 1)
    if m & (m >> 2):
        return True
    return False


class Position:
    """Board state.

    current : bitboard of stones belonging to the player TO MOVE
    mask    : bitboard of ALL stones (both players)
    moves   : number of stones played so far
    """

    def __init__(self):
        self.current = 0
        self.mask = 0
        self.moves = 0

    def copy(self):
        p = Position()
        p.current, p.mask, p.moves = self.current, self.mask, self.moves
        return p

    def can_play(self, col):
        return (self.mask & top_mask(col)) == 0

    def play(self, col):
        # Swap perspective: `current` becomes the stones of the player who
        # moves next (the opponent of whoever is playing right now).
        self.current ^= self.mask
        # Adding the bottom bit of the column to `mask` makes the carry
        # ripple up through the filled cells and set the first empty one.
        self.mask |= self.mask + bottom_mask(col)
        self.moves += 1

    def is_winning_move(self, col):
        """Would the player to move win by dropping a stone in `col`?"""
        new_stone = (self.mask + bottom_mask(col)) & column_mask(col)
        return alignment(self.current | new_stone)

    def key(self):
        """A single integer that uniquely identifies this position.

        `mask` says which cells are filled (so it encodes column heights),
        `current` says which of those belong to the player to move.
        Adding them gives a unique number per position, because the lowest
        empty cell of every column ends up marked by the carry.
        """
        return self.current + self.mask

    def possible(self):
        """Bitboard with a 1 on the lowest empty cell of every non-full column."""
        return (self.mask + BOTTOM_ALL) & BOARD_MASK

    def can_win_next(self):
        """True if the player to move has an immediate winning move."""
        return (winning_cells(self.current, self.mask) & self.possible()) != 0

    def possible_non_losing_moves(self):
        """Playable cells that do not hand the opponent an immediate win.

        Returns 0 if every move loses (so the position is lost).
        Assumes the player to move cannot win right now.
        """
        possible_mask = self.possible()
        opp_win = winning_cells(self.current ^ self.mask, self.mask)
        forced = possible_mask & opp_win
        if forced:
            if forced & (forced - 1):  # two or more threats: can't block both
                return 0
            possible_mask = forced  # one threat: we must block it
        # Never play directly under a cell where the opponent would win.
        return possible_mask & ~(opp_win >> 1)

    @staticmethod
    def from_moves(seq):
        """Build a position from a string of 1-indexed columns, e.g. '4453'."""
        p = Position()
        for ch in seq:
            col = int(ch) - 1
            if not (0 <= col < WIDTH) or not p.can_play(col):
                raise ValueError(f"illegal move {ch} in {seq!r}")
            if p.is_winning_move(col):
                raise ValueError(f"game already won before move {ch} in {seq!r}")
            p.play(col)
        return p

    def __str__(self):
        # Whose stones are which? After `moves` plies, the player to move is
        # 'X' if moves is even (first player), else 'O'.
        to_move = "X" if self.moves % 2 == 0 else "O"
        other = "O" if to_move == "X" else "X"
        rows = []
        for row in range(HEIGHT - 1, -1, -1):
            line = []
            for col in range(WIDTH):
                bit = 1 << (col * H1 + row)
                if self.current & bit:
                    line.append(to_move)
                elif self.mask & bit:
                    line.append(other)
                else:
                    line.append(".")
            rows.append(" ".join(line))
        return "\n".join(rows) + "\n" + " ".join(str(c + 1) for c in range(WIDTH))


# Search the center first: better ordering means more pruning.
COLUMN_ORDER = [3, 2, 4, 1, 5, 0, 6]

nodes_searched = 0


def negamax(p, alpha, beta):
    """Score of position `p` for the player to move.

    > 0 : player to move wins (bigger = faster win)
    0   : draw
    < 0 : player to move loses (more negative = faster loss)

    Score magnitude is (22 - number of stones the winner has played at the
    end of the game), so a win with your very last stone scores 1.
    """
    global nodes_searched
    nodes_searched += 1

    # Draw: board is full.
    if p.moves == WIDTH * HEIGHT:
        return 0

    # Can we win right now?
    for col in range(WIDTH):
        if p.can_play(col) and p.is_winning_move(col):
            return (WIDTH * HEIGHT + 1 - p.moves) // 2

    # We can't win this move, so the best possible score is a win on our
    # next move. Tighten beta to that upper bound.
    max_score = (WIDTH * HEIGHT - 1 - p.moves) // 2
    if beta > max_score:
        beta = max_score
        if alpha >= beta:
            return beta

    for col in COLUMN_ORDER:
        if p.can_play(col):
            child = p.copy()
            child.play(col)
            # The opponent's score is the negative of ours, and the
            # alpha-beta window flips and negates too.
            score = -negamax(child, -beta, -alpha)
            if score >= beta:
                return score  # beta cutoff: opponent will avoid this line
            if score > alpha:
                alpha = score
    return alpha


def solve(p):
    global nodes_searched
    nodes_searched = 0
    return negamax(p, -WIDTH * HEIGHT // 2, WIDTH * HEIGHT // 2)


def best_move(p):
    """Return (column, score) for the best move, 0-indexed column."""
    best_col, best_score = None, -10**9
    for col in COLUMN_ORDER:
        if not p.can_play(col):
            continue
        if p.is_winning_move(col):
            return col, (WIDTH * HEIGHT + 1 - p.moves) // 2
        child = p.copy()
        child.play(col)
        score = -solve_nw(child, negamax3)
        if score > best_score:
            best_col, best_score = col, score
    return best_col, best_score


# ---------------------------------------------------------------------------
# Stage 2: transposition table
# ---------------------------------------------------------------------------
# Different move orders reach the same position (playing 4 then 3 vs 3 then 4).
# We cache results so each position is searched once.
#
# Alpha-beta usually returns a BOUND, not the exact score, so we must store
# which kind of answer we got:
#   EXACT : the true score
#   LOWER : true score >= value (search failed high, hit a beta cutoff)
#   UPPER : true score <= value (search failed low, nothing beat alpha)

EXACT, LOWER, UPPER = 0, 1, 2
table = {}


def negamax_tt(p, alpha, beta):
    global nodes_searched
    nodes_searched += 1

    if p.moves == WIDTH * HEIGHT:
        return 0

    for col in range(WIDTH):
        if p.can_play(col) and p.is_winning_move(col):
            return (WIDTH * HEIGHT + 1 - p.moves) // 2

    max_score = (WIDTH * HEIGHT - 1 - p.moves) // 2
    if beta > max_score:
        beta = max_score
        if alpha >= beta:
            return beta

    # Look up what we already know about this position.
    key = p.key()
    entry = table.get(key)
    if entry is not None:
        value, flag = entry
        if flag == EXACT:
            return value
        if flag == LOWER:
            if value > alpha:
                alpha = value
        else:  # UPPER
            if value < beta:
                beta = value
        if alpha >= beta:
            return value

    original_alpha = alpha
    best = -WIDTH * HEIGHT
    for col in COLUMN_ORDER:
        if p.can_play(col):
            child = p.copy()
            child.play(col)
            score = -negamax_tt(child, -beta, -alpha)
            if score > best:
                best = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

    # Classify what the search proved, then cache it.
    if best <= original_alpha:
        table[key] = (best, UPPER)
    elif best >= beta:
        table[key] = (best, LOWER)
    else:
        table[key] = (best, EXACT)
    return best


def solve_tt(p):
    global nodes_searched
    nodes_searched = 0
    return negamax_tt(p, -WIDTH * HEIGHT // 2, WIDTH * HEIGHT // 2)


# ---------------------------------------------------------------------------
# Stage 3a: null-window search
# ---------------------------------------------------------------------------
# negamax(p, a, a+1) answers only "is the score <= a or > a?", which is much
# cheaper than computing the exact score. Binary search over the score range
# using these yes/no questions, and the table is shared between the passes.

def solve_nw(p, search=None, weak=False):
    """Exact score (or just win/draw/loss if weak=True) using null windows."""
    global nodes_searched
    if search is None:
        search = negamax3
    nodes_searched = 0
    lo = -((WIDTH * HEIGHT - p.moves) // 2)
    hi = (WIDTH * HEIGHT + 1 - p.moves) // 2
    if weak:
        lo, hi = -1, 1
    while lo < hi:
        med = lo + (hi - lo) // 2
        # Probe near 0 first: win/draw/loss questions prune the best.
        if med <= 0 and lo // 2 < med:
            med = lo // 2
        elif med >= 0 and hi // 2 > med:
            med = hi // 2
        r = search(p, med, med + 1)
        if r <= med:
            hi = r
        else:
            lo = r
    return lo


# ---------------------------------------------------------------------------
# Stage 3b: threat-aware pruning and move ordering
# ---------------------------------------------------------------------------
# 1. If we can win now, return immediately.
# 2. Drop moves that lose at once (letting the opponent win next turn). If a
#    single opponent threat exists we must block it; if two exist we lose.
# 3. Try moves that create the most winning cells for us first.

table3 = {}


def negamax3(p, alpha, beta):
    global nodes_searched
    nodes_searched += 1

    if p.can_win_next():
        return (WIDTH * HEIGHT + 1 - p.moves) // 2

    possible = p.possible_non_losing_moves()
    if possible == 0:
        # Every move lets the opponent win on their next turn.
        return -((WIDTH * HEIGHT - p.moves) // 2)

    if p.moves >= WIDTH * HEIGHT - 2:
        return 0  # nobody can win with at most two cells left

    # We can't win now, so the best case is winning next turn;
    # the opponent can't win now either, so the worst case is losing next turn.
    lo = -((WIDTH * HEIGHT - 2 - p.moves) // 2)
    if alpha < lo:
        alpha = lo
        if alpha >= beta:
            return alpha
    hi = (WIDTH * HEIGHT - 1 - p.moves) // 2
    if beta > hi:
        beta = hi
        if alpha >= beta:
            return beta

    key = p.key()
    entry = table3.get(key)
    if entry is not None:
        value, flag = entry
        if flag == EXACT:
            return value
        if flag == LOWER:
            if value > alpha:
                alpha = value
        else:
            if value < beta:
                beta = value
        if alpha >= beta:
            return value

    # Order: most threats created first; ties keep center-first order
    # because Python's sort is stable.
    moves = []
    for col in COLUMN_ORDER:
        m = possible & column_mask(col)
        if m:
            threats = popcount(winning_cells(p.current | m, p.mask | m))
            moves.append((threats, col))
    moves.sort(key=lambda t: -t[0])

    original_alpha = alpha
    best = -WIDTH * HEIGHT
    for _, col in moves:
        child = p.copy()
        child.play(col)
        score = -negamax3(child, -beta, -alpha)
        if score > best:
            best = score
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break

    if best <= original_alpha:
        table3[key] = (best, UPPER)
    elif best >= beta:
        table3[key] = (best, LOWER)
    else:
        table3[key] = (best, EXACT)
    return best


def solve3(p):
    """Full-window solve with the stage 3b search (no null windows)."""
    global nodes_searched
    nodes_searched = 0
    return negamax3(p, -WIDTH * HEIGHT // 2, WIDTH * HEIGHT // 2)


if __name__ == "__main__":
    import sys
    import time

    seq = sys.argv[1] if len(sys.argv) > 1 else "444444"
    pos = Position.from_moves(seq)
    print(pos)
    t = time.time()
    s = solve_nw(pos, negamax3)
    print(f"\nscore={s}  nodes={nodes_searched}  time={time.time() - t:.2f}s")
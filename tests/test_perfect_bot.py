"""Tests for the "perfect" Connect 4 bot (CPUPlayer / perf_bot.py).

Objectives covered:
  1. The bot plays the optimal move each turn.
  2. As the first player the bot always wins (checked with 2-bot games).

Run from anywhere with:  pytest tests -v
"""

import builtins
import itertools
import random
from functools import partial

import pytest

import perf_bot
from board import ConnectFourBoard
from game import ConnectFourGame
from player import AbstractPlayer, CPUPlayer

import oracle

ROWS, COLS = 6, 7


# ---------------------------------------------------------------- helpers

def legal_columns(board):
    return [c for c in range(COLS) if board.rows[0][c] == ' ']


def board_from_moves(moves):
    """Replay a move string (columns 1-7). Player 1 is 'X', player 2 is 'O'."""
    board = ConnectFourBoard(ROWS, COLS)
    for ply, ch in enumerate(moves):
        board.add_piece(int(ch) - 1, 'X' if ply % 2 == 0 else 'O')
    return board


class GuardedCPU(CPUPlayer):
    """The real CPUPlayer, but it fails the test instead of letting game.py
    loop forever when the bot picks an illegal column."""

    def move(self, **kwargs):
        col = super().move(**kwargs)
        board = kwargs['board']
        assert col in legal_columns(board), (
            f"bot chose illegal column {col} "
            f"at position {kwargs['position']!r}"
        )
        return col


class RandomBot(AbstractPlayer):
    def __init__(self, symbol, name, seed=0):
        super().__init__(symbol, name)
        self.rng = random.Random(seed)

    def move(self, **kwargs):
        return self.rng.choice(legal_columns(kwargs['board']))


class TacticalBot(RandomBot):
    """Takes an immediate win, blocks an immediate loss, otherwise random."""

    def move(self, **kwargs):
        board = kwargs['board']
        other = 'X' if self.symbol == 'O' else 'O'
        for who in (self.symbol, other):
            for col in legal_columns(board):
                row = board.get_landing_row(col)
                board.rows[row][col] = who
                won = board.check_winner()
                board.rows[row][col] = ' '
                if won:
                    return col
        return super().move(**kwargs)


class ScriptedBot(AbstractPlayer):
    """Plays a fixed list of columns, then random moves."""

    def __init__(self, symbol, name, script=(), seed=0):
        super().__init__(symbol, name)
        self.script = list(script)
        self.rng = random.Random(seed)

    def move(self, **kwargs):
        board = kwargs['board']
        if self.script:
            col = self.script.pop(0)
            if col in legal_columns(board):
                return col
        return self.rng.choice(legal_columns(board))


def play_game(monkeypatch, p2_type, p1_type=GuardedCPU):
    """Run a real ConnectFourGame (console mode) between two bots.

    Returns ('first' | 'second' | 'draw', final move string).
    """
    answers = iter(['X', 'y', 'O', 'y'])  # symbol + confirmation prompts
    monkeypatch.setattr(builtins, 'input', lambda *_: next(answers))

    game = ConnectFourGame('console', p1_type=p1_type, p2_type=p2_type)
    game.start()

    if not game.board.check_winner():
        return 'draw', game.position
    # Whoever moved last made the winning four.
    last_was_first = (len(game.position) % 2 == 1)
    return ('first' if last_was_first else 'second'), game.position


# ------------------------------------------------- objective 1: optimal moves

def test_opening_move_is_center_column():
    """Column 4 (index 3) is the only winning first move on 7x6."""
    board = ConnectFourBoard(ROWS, COLS)
    assert perf_bot.find_best_move(board, 'X', "") == 3


def test_takes_immediate_win_over_blocking():
    # X: 1,2,3 on the bottom row; O: 1,2,3 on the second row. Column 4 wins
    # for either side, and it is X's turn.
    moves = "112233"
    board = board_from_moves(moves)
    assert perf_bot.find_best_move(board, 'X', moves) == 3


def test_blocks_opponent_immediate_win():
    # O threatens 2,3,4 + column 5 on the bottom row. X has no win of its own.
    moves = "121364"
    board = board_from_moves(moves)
    assert perf_bot.find_best_move(board, 'X', moves) == 4


@pytest.mark.parametrize("opponent", [RandomBot, TacticalBot])
def test_bot_never_picks_illegal_column(monkeypatch, opponent):
    for seed in range(150):
        # GuardedCPU asserts legality on every single move.
        play_game(monkeypatch, partial(opponent, seed=seed))


@pytest.fixture(scope="module")
def solver():
    return oracle.Solver()


@pytest.mark.parametrize("opponent", [RandomBot, TacticalBot])
def test_every_bot_move_keeps_the_forced_win(solver, opponent):
    """Ground truth check: after each bot move the first player must still
    have a theoretical win (checked by an independent solver).

    Positions with fewer than 14 stones are skipped because solving them in
    pure Python takes minutes; those are covered by the win-rate tests.
    """
    checked = 0
    for seed in range(60):
        board = ConnectFourBoard(ROWS, COLS)
        opp = opponent(symbol='O', name='opp', seed=seed)
        bot = CPUPlayer(symbol='X', name='bot')
        position = ""
        for turn in range(ROWS * COLS):
            if turn % 2 == 0:
                col = bot.move(board=board, position=position)
                assert col in legal_columns(board)
            else:
                col = opp.move(board=board, position=position)
            board.add_piece(col, 'X' if turn % 2 == 0 else 'O')
            position += str(col + 1)
            if board.check_winner():
                break
            if turn % 2 == 0 and len(position) >= 14:
                checked += 1
                value = oracle.value_for_first_player_after(position, solver)
                assert value == 1, (
                    f"bot's move left a position that is no longer a forced "
                    f"win for player 1 (value {value}): {position}"
                )
    assert checked > 0


# ----------------------------------- objective 2: first player always wins

@pytest.mark.parametrize("opponent", [RandomBot, TacticalBot])
def test_first_player_bot_beats_second_bot(monkeypatch, opponent):
    results = []
    for seed in range(200):
        outcome, moves = play_game(monkeypatch, partial(opponent, seed=seed))
        results.append((outcome, moves))
    not_wins = [(o, m) for o, m in results if o != 'first']
    assert not not_wins, (
        f"{len(not_wins)}/{len(results)} games were not wins for the first "
        f"player, e.g. {not_wins[:3]}"
    )


def test_first_player_wins_against_every_opening_deviation(monkeypatch):
    """Opponent tries every possible sequence for its first three replies
    (7^3 = 343 lines), then plays tactically."""
    failures = []
    for i, script in enumerate(itertools.product(range(COLS), repeat=3)):
        outcome, moves = play_game(
            monkeypatch, partial(ScriptedBot, script=script, seed=i)
        )
        if outcome != 'first':
            failures.append((script, outcome, moves))
    assert not failures, (
        f"{len(failures)}/343 opponent openings did not lose, e.g. "
        f"{failures[:3]}"
    )

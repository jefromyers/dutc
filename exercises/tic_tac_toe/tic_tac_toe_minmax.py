import logging
from collections import deque
from itertools import cycle

from rich.logging import RichHandler

level = logging.DEBUG

logging.basicConfig(
    level=level,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("ttt")

# Copied Camron's TTT code:
# https://www.dontusethiscode.com/blog/2023-11-15_tictactoe_harder.html#traversal

from itertools import islice, tee


def nwise(iterable, n=2):
    return zip(*(islice(g, i, None) for i, g in enumerate(tee(iterable, n))))


def transpose(board):
    yield from zip(*board)


def flip_lr(board):
    yield from (r[::-1] for r in rows(board))


def rows(board):
    yield from (tuple(row) for row in board)


def columns(board):
    yield from transpose(board)


def major_diags(board):
    # above major diagonals
    for offset in range(1, len(board)):
        yield tuple(board[i][i - offset] for i in range(offset))

    # major diagonal
    yield tuple(row[i] for i, row in enumerate(rows(board)))

    # below diagonals
    for offset in reversed(range(1, len(board))):
        yield tuple(board[i - offset][i] for i in range(offset))


def minor_diags(board):
    yield from major_diags([*flip_lr(board)])


def traverse(board):
    for trav in [rows, columns, major_diags, minor_diags]:
        for i, group in enumerate(trav(board)):
            yield trav, i, group


def winner(line, ignore={"."}):
    uniq_line = set(line)
    if len(uniq_line) == 1 and uniq_line != ignore:
        return True, next(iter(uniq_line))
    return False, None


def find_winners(board, size=3):
    for trav, i, group in traverse(board):
        if len(group) < size:
            continue
        for offset, line in enumerate(nwise(group, n=size)):
            won, pl = winner(line)
            if won:
                yield trav, i, offset, pl


def move(player, board, loc):
    if board is None:
        board = [[".", ".", "."], [".", ".", "."], [".", ".", "."]]
    if board[loc[0]][loc[1]] != ".":
        logger.info("Invalid move")
        return
    board[loc[0]][loc[1]] = player
    return board


def render(board):
    logger.info(" ")
    for row in board:
        logger.info(" ".join(row))
    logger.info(" ")


if __name__ == "__main__":
    moves = deque(
        [
            (0, 0),  # x
            (1, 1),  # o
            (0, 1),  # x
            (1, 2),  # o
            (0, 2),  # x
            (2, 2),  # o
        ]
    )

    board = [[".", ".", "."], [".", ".", "."], [".", ".", "."]]
    players = ["x", "o"]
    for player in cycle(players):
        logger.info(f"{player}'s turn")
        try:
            loc = moves.popleft()
        except IndexError:
            break
        except Exception as e:
            logger.error(e)
            break

        board = move(player, board, loc)

        for trav, i, offset, pl in find_winners(board):
            logger.info(f"{pl!r} won on {trav.__name__: <8} {i}: {pl}")
            break

        render(board)

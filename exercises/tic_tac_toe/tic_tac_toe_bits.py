from itertools import cycle
from string import ascii_lowercase
from typing import List

winning_positions = [
    # rows
    0b111000000,
    0b000111000,
    0b000000111,
    # columns
    0b100100100,
    0b010010010,
    0b001001001,
    # diagonals
    0b100010001,
    0b001010100,
]


def won(board: int) -> bool:
    for pos in winning_positions:
        if board & pos == pos:
            return True
    return False


def cat(boards: List[int]) -> bool:
    combined = 0
    for board in boards:
        combined |= board

    return combined == 0b111111111


def move(boards: List[int], position: int, player: int) -> List[int]:
    if position < 1 or position > 9:
        raise ValueError("Must be between 1 and 9.")

    mask = 1 << (position - 1)

    for board in boards:
        if board & mask:
            raise ValueError("Position already taken.")

    boards[player] = boards[player] | mask

    return boards


def is_set(board: int, position: int) -> bool:
    if position < 1 or position > 9:
        raise ValueError("Must be between 1 and 9.")
    return (board & (1 << (position - 1))) != 0


def render(boards: List[int]) -> None:
    temp = """
     {0} | {1} | {2}
    -----------
     {3} | {4} | {5}
    -----------
     {6} | {7} | {8}
    """.format

    symbols = []
    for pos in range(1, 10):
        symbol = " "
        for idx, board in enumerate(boards):
            if is_set(board, pos):
                symbol = ascii_lowercase[idx]
                break
        symbols.append(symbol)

    print(temp(*symbols))


if __name__ == "__main__":
    # You can play with more than 2 players
    # boards = [0, 0, 0]

    boards = [0, 0]
    render(boards)
    for player in cycle(range(len(boards))):
        print(f"Player {player}'s turn.")
        pos = int(input("Enter a position: "))

        try:
            boards = move(boards, pos, player)
            render(boards)

            if won(boards[player]):
                print(f"Player {player} won 🎉!\n\n\n")
                break
            elif cat(boards):
                print("Cat!")
                break
        except ValueError as e:
            print(f"Skiping you're turn: {e}")
            continue

        print(f"Save boards to file: {boards}")

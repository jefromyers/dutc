import logging
from dataclasses import dataclass, field
from enum import Enum
from itertools import cycle
from socket import AF_INET, SOCK_STREAM, socket
from string import ascii_lowercase
from typing import List

from rich.logging import RichHandler

level = logging.DEBUG

logging.basicConfig(
    level=level,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

BOARD_TEMPLATE = """
 {0} | {1} | {2}
-----------
 {3} | {4} | {5}
-----------
 {6} | {7} | {8}\n
""".format


class Conditions(Enum):
    WON = "won"
    CAT = "cat"

    def __str__(self):
        return self.value


@dataclass
class Rules:
    winning_conditions: list = field(default_factory=list)
    # XXX: We could get weird and have losing conditions maybe?

    def won(self, board: int) -> bool:
        for pos in self.winning_conditions:
            if board & pos == pos:
                return True
        return False

    # XXX: It would be neat to be able to pass arbitrary function in that were
    # part of the rules
    def cat(self, boards: List[int]) -> bool:
        combined = 0
        for board in boards:
            combined |= board

        return combined == 0b111111111


@dataclass
class Player:
    conn: socket
    addr: str
    name: str = "Larry"
    _board: int = 0

    @classmethod
    def from_socket(cls, client: tuple):
        conn, addr = client
        return cls(conn, addr)

    def is_set(self, position: int) -> bool:
        if position < 1 or position > 9:
            raise ValueError("Must be between 1 and 9.")
        return (self._board & (1 << (position - 1))) != 0


@dataclass
class Game:
    rules: Rules
    min_players: int = 2
    max_players: int = 3  # XXX: Maybe for future games with more then 2 players
    _players: list = field(default_factory=list)
    _winner: str | None = (
        None  # XXX: We should probably use a Player & make Cat a player
    )

    def _move(self, position: int, player_board: int) -> int:
        if position < 1 or position > 9:
            raise ValueError("Must be between 1 and 9.")

        mask = 1 << (position - 1)

        boards = [p._board for p in self._players]
        for board in boards:
            if board & mask:
                raise ValueError("Position already taken.")

        new_board = player_board | mask

        return new_board

    def init(self) -> None:
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(("0.0.0.0", 4227))
        server.listen(self.max_players)

        while len(self._players) < self.max_players:
            player = Player.from_socket(server.accept())
            player.conn.sendall(b"Welcome to Tic Tac Toe!\nWhat is your name?\n")
            player.name = player.conn.recv(1024).decode().strip()
            self._players.append(player)
            logging.info(f"Player {len(self._players)} connected from {player.addr}")
            if len(self._players) >= self.min_players:
                logging.info("Minimum number of players reached. Lets playn now.")
                break

        self.play()
        server.close()

    def play(self) -> None:
        for pn in cycle(range(len(self._players))):
            player = self._players[pn]
            msg = f"{player.name}'s turn\nCurrent board:\n{self}"
            logging.info(msg)
            self.message(msg)
            try:
                pos = int(player.conn.recv(1024).decode())
                player._board = self._move(pos, player._board)
            except Exception as e:
                # XXX: We could imrpove this error handling
                msg = f"Invalid move by {player.name}: {e}"
                self.message(msg)
                logging.info(msg)
                continue

            if resolved := self._won_or_cat(player):
                match resolved:
                    case Conditions.WON:
                        logging.info(f"Player {pn} won!")
                        self._winner = player.name
                    case Conditions.CAT:
                        logging.info(f"Meow the cat won!")
                        self._winner = "Cat"
                    case _:
                        logging.info(f"Well, how did I get here?")
                break

        self.end_game()

    def _won_or_cat(self, player) -> Conditions | None:
        if self.rules.cat([p._board for p in self._players]):
            return Conditions.CAT
        if self.rules.won(player._board):
            return Conditions.WON

        return None

    def __str__(self) -> str:
        symbols = []
        for pos in range(1, 10):
            symbol = " "
            for idx, player in enumerate([p for p in self._players]):
                if player.is_set(pos):
                    symbol = ascii_lowercase[idx]
                    break
            symbols.append(symbol)

        return BOARD_TEMPLATE(*symbols)

    def message(self, msg: str) -> None:
        for player in self._players:
            player.conn.sendall(msg.encode())

    def end_game(self) -> None:
        msg = f"Game over! {self._winner} won!\n{self}\nThanks for playing!\n"
        logging.info(msg)
        self.message(msg)

        for p in self._players:
            p.conn.close()


if __name__ == "__main__":
    # TODO: We should print out the rules, the board numbers, etc...
    # nc localhost 4227 to play
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
    rules = Rules(winning_conditions=winning_positions)
    game = Game(rules)
    game.init()

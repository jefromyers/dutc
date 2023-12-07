import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from random import Random
from typing import Dict

from rich.logging import RichHandler

level = logging.DEBUG

logging.basicConfig(
    level=level,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)


def get_word():
    with open("/usr/share/dict/words") as f:
        wordlist = (ln.strip() for ln in f)
        wordlist = {w for w in wordlist if w.isalpha() and w.islower()}

    rnd = Random(0)
    answer = rnd.choice(sorted(wordlist))  # supermarket on a Ubuntu
    return answer


class Message(Enum):
    GUESS = "guess"
    REQUEST = "request"
    CONFIRM = "confirm"

    def __init__(self, label: str):
        self.label = label
        self.data = {}

    @classmethod
    def with_data(cls, data: Dict[str, str]):
        inst = cls("guess")
        inst.data = data
        return inst


@dataclass
class Player:
    name: str
    tires: int = 10

    def __str__(self):
        return f"{self.name} - {self.tires} tries left"


@dataclass
class Action:
    player: Player
    message: Message


@dataclass
class State:
    answer: str
    players: list = field(default_factory=list)
    confirmed: list = field(default_factory=list)
    guesses: list = field(default_factory=list)
    preformed: str = "nothing"
    winner: Player | None = None
    _penalty: list = field(default_factory=list)


@dataclass
class Game:
    def __init__(self, answer):
        self.state = State(answer=answer)

    def _validate_action(self, action):
        logger.debug(f"validating action {action}")
        if not isinstance(action, Action):
            logger.error("not an action")
            return False
        if not isinstance(action.message, Message):
            logger.error("not a message")
            return False
        if not isinstance(action.player, Player):
            logger.error("not a player")
            return False
        return True

    def _confirmed(self, player):
        return player in self.state.confirmed

    def _penalized(self, player):
        # TODO: write penalty logic
        return False

    def process(self, action):
        if not self._validate_action(action):
            self.state.preformed = "invalid action"
            return

        match action.message:
            case Message.REQUEST:
                if action.player in self.state.players:
                    self.state.preformed = (
                        f"{action.player.name} already joined, skipping turn"
                    )
                self.state.players.append(action.player)
                self.state.preformed = f"{action.player.name} joined"
            case Message.CONFIRM:
                if (
                    self._confirmed(action.player)
                    or action.player in self.state.players
                ):
                    self.state.confirmed.append(action.player)
                    self.state.preformed = f"{action.player.name} confirmed"
                else:
                    self.state.preformed = (
                        f"{action.player.name} not confirmed, skipping turn"
                    )
            case Message.GUESS:
                if not self._confirmed(action.player):
                    self.state.preformed = (
                        f"{action.player.name} not confirmed, skipping turn"
                    )
                    return
                if self._penalized(action.player):
                    self.state.preformed = (
                        f"{action.player.name} penalized, skipping turn"
                    )
                    return
                if action.message.data["word"] == self.state.answer:
                    logger.debug(f"{action.player.name} won!")
                    self.state.winner = action.player
                    self.state.preformed = f"{action.player.name} won!"
                    return self.state
                if action.message.data["word"] in self.state.guesses:
                    self.state.preformed = (
                        f"{action.player.name} already guessed this word"
                    )
                    self.state._penalty[action.player] = time.time()
                    action.player.tires -= 1
                    return
                action.player.tires -= 1
                self.state.guesses.append(action.message.data["word"])
            case _:
                self.state.preformed = f"unknown message {action.message.label}"

    def simulate(self):
        while True:
            action = yield self.state
            if action is None:
                continue
            self.process(action)


if __name__ == "__main__":
    iris = Player("Iris")
    dad = Player("Dad")
    actions = deque(
        [
            Action(iris, Message.REQUEST),
            Action(dad, Message.REQUEST),
            Action(iris, Message.CONFIRM),
            Action(dad, Message.CONFIRM),
            Action(dad, Message.GUESS.with_data({"word": "supermarket"})),
        ]
    )
    answer = get_word()
    game = Game(answer).simulate()
    for _ in game:
        try:
            resp = game.send(actions.popleft())
            logger.info(resp)
            if resp.winner:
                logger.info(f"{resp.winner.name} won 🎉🎉🎉")
                exit(0)
        except IndexError:
            break
        except StopIteration:
            break

        input("→")

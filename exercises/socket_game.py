import logging
import socket
from random import Random
from threading import Thread
from time import sleep

from rich.logging import RichHandler

level = logging.DEBUG

logging.basicConfig(
    level=level,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)

rnd = Random(0)


def client_game(conn, answer):
    # We could pass in all the other players and let them know they'v lost if
    # the correct answer is guessed
    conn.sendall(b"Guess a number between 1 and 10\n")
    while True:
        try:
            guess = conn.recv(1024).strip()
            logger.info(f"Received {guess}")
            if guess:
                if int(guess) == answer:
                    conn.sendall(b"You win!")
                    break
                else:
                    conn.sendall(b"Nope, try again\n")
        except ConnectionResetError:
            logger.error("Connection reset")
            break
        except Exception as e:
            logger.error(e)
            break


def main():
    max_players = 3
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4227))
    server.listen(max_players)

    answer = rnd.randint(1, 10)

    players = []
    while len(players) < max_players:
        logger.info(f"Waiting for player {len(players) + 1}")
        conn, address = server.accept()
        players.append((conn, address))
        logger.info(f"Player {len(players)} connected")

        # Lets let people know they're waiting
        for conn, _ in players:
            conn.sendall(b"Waiting for more players\n")

        sleep(1)

    logger.info(f"All players connected, starting game answer is {answer} 🎉\n")
    threads = []
    for conn, _ in players:
        t = Thread(target=client_game, args=(conn, answer))
        threads.append(t)
        t.start()

    # Wait for everyone to guess right. Maybe we could then tell them their
    # rank...
    for t in threads:
        t.join()

    logger.info("Game over")


if __name__ == "__main__":
    # nc localhost 4227 to play
    main()

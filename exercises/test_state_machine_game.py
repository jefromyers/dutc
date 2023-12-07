import pytest
from state_machine_game import Message


def test_smokem_if_you_got_em():
    assert True == True


def test_guess_message_with_data():
    guess_message = Message.GUESS.with_data({"word": "apple"})

    assert guess_message == Message.GUESS
    assert guess_message.data["word"] == "apple"

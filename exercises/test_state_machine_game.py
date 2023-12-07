import pytest
from state_machine_game import Message


def test_smokem_if_you_got_em():
    assert True == True


def test_message_with_data():
    guess_message = Message.GUESS.with_data({"word": "apple"})

    assert guess_message.label == Message.GUESS.value
    assert guess_message.data == {"word": "apple"}


def test_message_enum_value():
    assert Message.GUESS.value == "guess"
    assert Message.REQUEST.value == "request"
    assert Message.CONFIRM.value == "confirm"

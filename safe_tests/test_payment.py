from datetime import datetime
from app.cart.routes import luhn_check, card_not_expired


def test_valid_card():
    assert luhn_check("4242424242424242") is True


def test_invalid_card():
    assert luhn_check("1234567890123456") is False


def test_card_not_expired_future_year():
    future_year = datetime.now().year + 1
    assert card_not_expired(12, future_year) is True

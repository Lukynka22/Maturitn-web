from datetime import datetime
from test_utils.payment_utils import luhn_check, card_not_expired, is_valid_cvc


def test_valid_card():
    assert luhn_check("4242424242424242") is True


def test_invalid_card():
    assert luhn_check("1234567890123456") is False


def test_card_not_expired_future_year():
    future_year = datetime.now().year + 1
    assert card_not_expired(12, future_year) is True


def test_cvc_max_3_digits():
    assert is_valid_cvc("123") is True
    assert is_valid_cvc("12") is True
    assert is_valid_cvc("") is True
    assert is_valid_cvc("1234") is False
    assert is_valid_cvc("12a") is False

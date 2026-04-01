from datetime import datetime


def luhn_check(card_number: str) -> bool:
    if not card_number.isdigit():
        return False

    total = 0
    reversed_digits = card_number[::-1]

    for i, digit in enumerate(reversed_digits):
        number = int(digit)

        if i % 2 == 1:
            number *= 2
            if number > 9:
                number -= 9

        total += number

    return total % 10 == 0


def card_not_expired(month: int, year: int) -> bool:
    now = datetime.now()
    return year > now.year or (year == now.year and month >= now.month)


def is_valid_cvc(cvc: str) -> bool:
    if cvc == "":
        return True
    return cvc.isdigit() and len(cvc) <= 3

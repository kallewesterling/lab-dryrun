"""ISBN helpers: clean up, validate and convert ISBN-10 and ISBN-13 numbers."""

from __future__ import annotations


class InvalidISBNError(ValueError):
    """Raised when a string isn't a valid ISBN-10 or ISBN-13."""


def normalize(raw: str) -> str:
    """Strip spaces and hyphens, and upper-case a trailing 'x'."""
    cleaned = raw.replace("-", "").replace(" ", "").strip()
    return cleaned.upper()


def isbn10_check_digit(first_nine: str) -> str:
    """Return the check digit for the first nine digits of an ISBN-10."""
    if len(first_nine) != 9 or not first_nine.isdigit():
        raise InvalidISBNError(f"expected 9 digits, got {first_nine!r}")
    total = sum((10 - i) * int(d) for i, d in enumerate(first_nine))
    check = (11 - total % 11) % 11
    return "X" if check == 10 else str(check)


def isbn13_check_digit(first_twelve: str) -> str:
    """Return the check digit for the first twelve digits of an ISBN-13."""
    if len(first_twelve) != 12 or not first_twelve.isdigit():
        raise InvalidISBNError(f"expected 12 digits, got {first_twelve!r}")
    total = sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(first_twelve))
    return str((10 - total % 10) % 10)


def is_valid_isbn10(value: str) -> bool:
    value = normalize(value)
    if len(value) != 10 or not value[:9].isdigit():
        return False
    if not (value[9].isdigit() or value[9] == "X"):
        return False
    return isbn10_check_digit(value[:9]) == value[9]


def is_valid_isbn13(value: str) -> bool:
    value = normalize(value)
    if len(value) != 13 or not value.isdigit():
        return False
    if not value.startswith(("978", "979")):
        return False
    return isbn13_check_digit(value[:12]) == value[12]


def to_isbn13(value: str) -> str:
    """Return the ISBN-13 form of a valid ISBN-10 or ISBN-13."""
    value = normalize(value)
    if is_valid_isbn13(value):
        return value
    if is_valid_isbn10(value):
        first_twelve = "978" + value[:9]
        return first_twelve + isbn13_check_digit(first_twelve)
    raise InvalidISBNError(f"not a valid ISBN: {value!r}")

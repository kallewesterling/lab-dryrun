from __future__ import annotations

import pytest

from bookshelf.isbn import (
    InvalidISBNError,
    is_valid_isbn10,
    is_valid_isbn13,
    isbn10_check_digit,
    isbn13_check_digit,
    normalize,
    to_isbn13,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("978-0-441-17271-9", "9780441172719"),
        (" 0 441 17271 7 ", "0441172717"),
        ("080442957x", "080442957X"),
        ("9780441172719", "9780441172719"),
    ],
)
def test_normalize(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


@pytest.mark.parametrize(
    ("first_nine", "expected"),
    [("044117271", "7"), ("080442957", "X"), ("030640615", "2")],
)
def test_isbn10_check_digit(first_nine: str, expected: str) -> None:
    assert isbn10_check_digit(first_nine) == expected


@pytest.mark.parametrize(
    ("first_twelve", "expected"),
    [("978044117271", "9"), ("978030640615", "7"), ("979100000000", "8")],
)
def test_isbn13_check_digit(first_twelve: str, expected: str) -> None:
    assert isbn13_check_digit(first_twelve) == expected


@pytest.mark.parametrize("bad", ["", "12345", "abcdefghi", "0441172717"])
def test_isbn13_check_digit_rejects_bad_input(bad: str) -> None:
    with pytest.raises(InvalidISBNError):
        isbn13_check_digit(bad)


@pytest.mark.parametrize("value", ["0441172717", "080442957X", "0-306-40615-2"])
def test_valid_isbn10(value: str) -> None:
    assert is_valid_isbn10(value)


@pytest.mark.parametrize("value", ["0441172718", "080442957Y", "12345", "X441172717"])
def test_invalid_isbn10(value: str) -> None:
    assert not is_valid_isbn10(value)


@pytest.mark.parametrize("value", ["9780441172719", "978-0-306-40615-7", "9791000000008"])
def test_valid_isbn13(value: str) -> None:
    assert is_valid_isbn13(value)


@pytest.mark.parametrize(
    "value",
    ["9780441172718", "9770441172719", "978044117271", "97804411727190", "97804411727a9"],
)
def test_invalid_isbn13(value: str) -> None:
    assert not is_valid_isbn13(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0441172717", "9780441172719"),
        ("0-306-40615-2", "9780306406157"),
        ("9780441172719", "9780441172719"),
    ],
)
def test_to_isbn13(value: str, expected: str) -> None:
    assert to_isbn13(value) == expected


@pytest.mark.parametrize("value", ["", "not an isbn", "9780441172718"])
def test_to_isbn13_rejects_invalid(value: str) -> None:
    with pytest.raises(InvalidISBNError):
        to_isbn13(value)

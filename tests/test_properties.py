"""Property-based tests. Hypothesis tries many generated inputs for each test."""

from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from bookshelf.isbn import (  # noqa: E402
    is_valid_isbn10,
    is_valid_isbn13,
    isbn10_check_digit,
    isbn13_check_digit,
    normalize,
    to_isbn13,
)
from bookshelf.store import BookStore  # noqa: E402

pytestmark = pytest.mark.property

nine_digits = st.text(alphabet="0123456789", min_size=9, max_size=9)
twelve_digits = st.text(alphabet="0123456789", min_size=9, max_size=9).map(lambda s: "978" + s)


@given(nine_digits)
def test_isbn10_with_its_check_digit_is_valid(first_nine: str) -> None:
    assert is_valid_isbn10(first_nine + isbn10_check_digit(first_nine))


@given(twelve_digits)
def test_isbn13_with_its_check_digit_is_valid(first_twelve: str) -> None:
    assert is_valid_isbn13(first_twelve + isbn13_check_digit(first_twelve))


@given(twelve_digits, st.integers(min_value=0, max_value=11), st.integers(min_value=1, max_value=9))
def test_changing_one_digit_breaks_isbn13(first_twelve: str, position: int, delta: int) -> None:
    valid = first_twelve + isbn13_check_digit(first_twelve)
    changed_digit = str((int(valid[position]) + delta) % 10)
    tampered = valid[:position] + changed_digit + valid[position + 1 :]
    assert not is_valid_isbn13(tampered)


@given(nine_digits)
def test_isbn10_converts_to_valid_isbn13(first_nine: str) -> None:
    isbn10 = first_nine + isbn10_check_digit(first_nine)
    isbn13 = to_isbn13(isbn10)
    assert is_valid_isbn13(isbn13)
    assert isbn13[3:12] == first_nine
    assert to_isbn13(isbn13) == isbn13


@given(st.text(alphabet="0123456789-x ", max_size=20))
def test_normalize_is_idempotent(raw: str) -> None:
    assert normalize(normalize(raw)) == normalize(raw)


@given(st.lists(nine_digits, min_size=1, max_size=20, unique=True))
def test_store_ids_are_unique_and_lookups_round_trip(prefixes: list[str]) -> None:
    store = BookStore()
    books = [
        store.add(
            title=f"Book {i}",
            author="Author",
            isbn=p + isbn10_check_digit(p),
            year=2000,
        )
        for i, p in enumerate(prefixes)
    ]
    assert len({b.id for b in books}) == len(books)
    assert all(store.get(b.id) == b for b in books)

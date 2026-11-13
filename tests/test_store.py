from __future__ import annotations

import pytest

from bookshelf.store import BookNotFoundError, BookStore, DuplicateISBNError

from .conftest import DUNE, EARTHSEA, NEUROMANCER


def test_add_assigns_ids_and_normalises(store: BookStore) -> None:
    book = store.add(
        title="  Dune  ", author="Frank   Herbert", isbn="0441172717", year=1965, tags=["Sci-Fi"]
    )
    assert book.id == 1
    assert book.title == "Dune"
    assert book.author == "Frank Herbert"
    assert book.isbn == DUNE
    assert book.tags == ("sci-fi",)


def test_add_rejects_duplicate_isbn(filled_store: BookStore) -> None:
    with pytest.raises(DuplicateISBNError):
        filled_store.add(title="Dune again", author="Someone", isbn="0441172717", year=2000)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "x" * 201),
        ("author", "   "),
        ("isbn", "123"),
        ("year", 1200),
        ("year", 2200),
        ("year", True),
    ],
)
def test_add_rejects_bad_values(store: BookStore, field: str, value: object) -> None:
    book: dict[str, object] = {
        "title": "Title",
        "author": "Author",
        "isbn": NEUROMANCER,
        "year": 1984,
    }
    book[field] = value
    with pytest.raises(ValueError):
        store.add(**book)  # type: ignore[arg-type]


def test_get_and_delete(filled_store: BookStore) -> None:
    assert filled_store.get(1).title == "Dune"
    filled_store.delete(1)
    with pytest.raises(BookNotFoundError):
        filled_store.get(1)
    with pytest.raises(BookNotFoundError):
        filled_store.delete(1)
    assert len(filled_store) == 2


def test_update_changes_only_given_fields(filled_store: BookStore) -> None:
    updated = filled_store.update(2, year=1985, tags=["Classic"])
    assert updated.year == 1985
    assert updated.tags == ("classic",)
    assert updated.title == "Neuromancer"
    assert filled_store.get(2) == updated


def test_update_rejects_read_only_fields(filled_store: BookStore) -> None:
    with pytest.raises(ValueError, match="isbn"):
        filled_store.update(1, isbn=EARTHSEA)


def test_list_is_sorted_by_author(filled_store: BookStore) -> None:
    assert [b.author for b in filled_store.list()] == [
        "Frank Herbert",
        "Ursula K. Le Guin",
        "William Gibson",
    ]


@pytest.mark.parametrize(
    ("kwargs", "titles"),
    [
        ({"author": "william gibson"}, ["Neuromancer"]),
        ({"tag": "SCI-FI"}, ["Dune", "Neuromancer"]),
        ({"query": "earth"}, ["A Wizard of Earthsea"]),
        ({"query": "herbert"}, ["Dune"]),
        ({"limit": 1, "offset": 1}, ["A Wizard of Earthsea"]),
        ({"tag": "romance"}, []),
    ],
)
def test_list_filters(
    filled_store: BookStore, kwargs: dict[str, object], titles: list[str]
) -> None:
    assert [b.title for b in filled_store.list(**kwargs)] == titles  # type: ignore[arg-type]


@pytest.mark.parametrize(("limit", "offset"), [(0, 0), (101, 0), (10, -1)])
def test_list_rejects_bad_paging(filled_store: BookStore, limit: int, offset: int) -> None:
    with pytest.raises(ValueError):
        filled_store.list(limit=limit, offset=offset)

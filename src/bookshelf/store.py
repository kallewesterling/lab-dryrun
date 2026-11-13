"""An in-memory store of books. Good enough for a demo; nothing is persisted."""

from __future__ import annotations

import itertools
import threading
from dataclasses import asdict, dataclass, field, replace
from typing import Any

from bookshelf.isbn import InvalidISBNError, to_isbn13


class BookNotFoundError(KeyError):
    """Raised when no book has the requested id."""


class DuplicateISBNError(ValueError):
    """Raised when a book with the same ISBN is already on the shelf."""


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str
    isbn: str
    year: int
    tags: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tags"] = list(self.tags)
        return data


def _clean_text(value: str, name: str) -> str:
    cleaned = " ".join(value.split())
    if not cleaned:
        raise ValueError(f"{name} must not be empty")
    if len(cleaned) > 200:
        raise ValueError(f"{name} must be at most 200 characters")
    return cleaned


def _clean_year(year: int) -> int:
    if isinstance(year, bool) or not isinstance(year, int):
        raise ValueError("year must be an integer")
    if not 1450 <= year <= 2100:
        raise ValueError("year must be between 1450 and 2100")
    return year


def _clean_tags(tags: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    cleaned = {_clean_text(tag, "tag").lower() for tag in tags}
    return tuple(sorted(cleaned))


class BookStore:
    def __init__(self) -> None:
        self._books: dict[int, Book] = {}
        self._ids = itertools.count(1)
        self._lock = threading.Lock()

    def __len__(self) -> int:
        return len(self._books)

    def add(
        self,
        *,
        title: str,
        author: str,
        isbn: str,
        year: int,
        tags: list[str] | tuple[str, ...] = (),
    ) -> Book:
        try:
            isbn13 = to_isbn13(isbn)
        except InvalidISBNError as exc:
            raise ValueError(str(exc)) from exc
        with self._lock:
            if any(book.isbn == isbn13 for book in self._books.values()):
                raise DuplicateISBNError(f"a book with ISBN {isbn13} is already on the shelf")
            book = Book(
                id=next(self._ids),
                title=_clean_text(title, "title"),
                author=_clean_text(author, "author"),
                isbn=isbn13,
                year=_clean_year(year),
                tags=_clean_tags(tags),
            )
            self._books[book.id] = book
        return book

    def get(self, book_id: int) -> Book:
        try:
            return self._books[book_id]
        except KeyError:
            raise BookNotFoundError(book_id) from None

    def update(self, book_id: int, **changes: Any) -> Book:
        book = self.get(book_id)
        cleaned: dict[str, Any] = {}
        if "title" in changes:
            cleaned["title"] = _clean_text(changes.pop("title"), "title")
        if "author" in changes:
            cleaned["author"] = _clean_text(changes.pop("author"), "author")
        if "year" in changes:
            cleaned["year"] = _clean_year(changes.pop("year"))
        if "tags" in changes:
            cleaned["tags"] = _clean_tags(changes.pop("tags"))
        if changes:
            raise ValueError(f"unknown or read-only fields: {', '.join(sorted(changes))}")
        updated = replace(book, **cleaned)
        with self._lock:
            self._books[book_id] = updated
        return updated

    def delete(self, book_id: int) -> None:
        with self._lock:
            if self._books.pop(book_id, None) is None:
                raise BookNotFoundError(book_id)

    def list(
        self,
        *,
        author: str | None = None,
        tag: str | None = None,
        query: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]:
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        if offset < 0:
            raise ValueError("offset must not be negative")
        books = sorted(self._books.values(), key=lambda b: (b.author.lower(), b.year, b.title))
        if author is not None:
            books = [b for b in books if b.author.lower() == author.lower()]
        if tag is not None:
            books = [b for b in books if tag.lower() in b.tags]
        if query is not None:
            needle = query.lower()
            books = [b for b in books if needle in b.title.lower() or needle in b.author.lower()]
        return books[offset : offset + limit]

"""Bookshelf: a small REST API for the Chainguard Learning Lab sample repo."""

from bookshelf.app import create_app
from bookshelf.store import Book, BookStore

__all__ = ["Book", "BookStore", "create_app"]
__version__ = "0.1.0"

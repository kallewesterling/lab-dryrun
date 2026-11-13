"""The HTTP API: a small Flask app on top of the in-memory BookStore."""

from __future__ import annotations

from typing import Any

from flask import Flask, Response, jsonify, request

from bookshelf.store import BookNotFoundError, BookStore, DuplicateISBNError

REQUIRED_FIELDS = ("title", "author", "isbn", "year")


def _error(message: str, status: int) -> tuple[Response, int]:
    return jsonify({"error": message}), status


def _json_body() -> dict[str, Any] | None:
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def _int_arg(name: str, default: int) -> int:
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{name} must be an integer") from None


def _optional_int_arg(name: str) -> int | None:
    if request.args.get(name) is None:
        return None
    return _int_arg(name, 0)


def create_app(store: BookStore | None = None) -> Flask:
    app = Flask(__name__)
    shelf = store if store is not None else BookStore()

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok", "books": len(shelf)})

    @app.get("/books")
    def list_books() -> Response | tuple[Response, int]:
        try:
            books = shelf.list(
                author=request.args.get("author"),
                tag=request.args.get("tag"),
                query=request.args.get("q"),
                year_from=_optional_int_arg("year_from"),
                limit=_int_arg("limit", 20),
                offset=_int_arg("offset", 0),
            )
        except ValueError as exc:
            return _error(str(exc), 400)
        return jsonify({"books": [b.to_dict() for b in books], "count": len(books)})

    @app.post("/books")
    def add_book() -> tuple[Response, int]:
        body = _json_body()
        if body is None:
            return _error("request body must be a JSON object", 400)
        missing = [name for name in REQUIRED_FIELDS if name not in body]
        if missing:
            return _error(f"missing fields: {', '.join(missing)}", 400)
        try:
            book = shelf.add(
                title=body["title"],
                author=body["author"],
                isbn=body["isbn"],
                year=body["year"],
                tags=body.get("tags", []),
            )
        except DuplicateISBNError as exc:
            return _error(str(exc), 409)
        except (TypeError, ValueError, AttributeError) as exc:
            return _error(str(exc), 400)
        return jsonify(book.to_dict()), 201

    @app.get("/books/<int:book_id>")
    def get_book(book_id: int) -> Response | tuple[Response, int]:
        try:
            return jsonify(shelf.get(book_id).to_dict())
        except BookNotFoundError:
            return _error(f"no book with id {book_id}", 404)

    @app.patch("/books/<int:book_id>")
    def update_book(book_id: int) -> Response | tuple[Response, int]:
        body = _json_body()
        if body is None:
            return _error("request body must be a JSON object", 400)
        try:
            return jsonify(shelf.update(book_id, **body).to_dict())
        except BookNotFoundError:
            return _error(f"no book with id {book_id}", 404)
        except (TypeError, ValueError, AttributeError) as exc:
            return _error(str(exc), 400)

    @app.delete("/books/<int:book_id>")
    def delete_book(book_id: int) -> tuple[str, int] | tuple[Response, int]:
        try:
            shelf.delete(book_id)
        except BookNotFoundError:
            return _error(f"no book with id {book_id}", 404)
        return "", 204

    return app

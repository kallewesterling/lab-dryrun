from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from .conftest import DUNE

pytestmark = pytest.mark.integration


def test_health(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "books": 3}


def test_list_books(client: FlaskClient) -> None:
    response = client.get("/books")
    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == 3
    assert body["books"][0]["title"] == "Dune"


@pytest.mark.parametrize(
    ("query", "titles"),
    [
        ("?author=Frank%20Herbert", ["Dune"]),
        ("?tag=cyberpunk", ["Neuromancer"]),
        ("?q=wizard", ["A Wizard of Earthsea"]),
        ("?limit=2", ["Dune", "A Wizard of Earthsea"]),
    ],
)
def test_list_books_filters(client: FlaskClient, query: str, titles: list[str]) -> None:
    body = client.get(f"/books{query}").get_json()
    assert [b["title"] for b in body["books"]] == titles


@pytest.mark.parametrize("query", ["?limit=abc", "?limit=0", "?offset=-5"])
def test_list_books_bad_paging(client: FlaskClient, query: str) -> None:
    assert client.get(f"/books{query}").status_code == 400


def test_add_book(client: FlaskClient) -> None:
    response = client.post(
        "/books",
        json={
            "title": "The Left Hand of Darkness",
            "author": "Ursula K. Le Guin",
            "isbn": "0-441-47812-3",
            "year": 1969,
            "tags": ["sci-fi"],
        },
    )
    assert response.status_code == 201
    book = response.get_json()
    assert book["id"] == 4
    assert book["isbn"] == "9780441478125"
    assert client.get("/health").get_json()["books"] == 4


@pytest.mark.parametrize(
    ("payload", "status"),
    [
        ({"title": "No ISBN", "author": "A", "year": 2000}, 400),
        ({"title": "Bad ISBN", "author": "A", "isbn": "123", "year": 2000}, 400),
        ({"title": "Dupe", "author": "A", "isbn": DUNE, "year": 2000}, 409),
        ({"title": "Bad year", "author": "A", "isbn": "0306406152", "year": "soon"}, 400),
    ],
)
def test_add_book_errors(client: FlaskClient, payload: dict[str, object], status: int) -> None:
    assert client.post("/books", json=payload).status_code == status


def test_add_book_requires_json_object(client: FlaskClient) -> None:
    assert client.post("/books", data="not json", content_type="text/plain").status_code == 400
    assert client.post("/books", json=["a", "list"]).status_code == 400


def test_get_book(client: FlaskClient) -> None:
    assert client.get("/books/1").get_json()["title"] == "Dune"
    assert client.get("/books/99").status_code == 404


def test_update_book(client: FlaskClient) -> None:
    response = client.patch("/books/3", json={"tags": ["fantasy", "classic"]})
    assert response.status_code == 200
    assert response.get_json()["tags"] == ["classic", "fantasy"]
    assert client.patch("/books/3", json={"isbn": DUNE}).status_code == 400
    assert client.patch("/books/99", json={"year": 2000}).status_code == 404


def test_delete_book(client: FlaskClient) -> None:
    assert client.delete("/books/2").status_code == 204
    assert client.get("/books/2").status_code == 404
    assert client.delete("/books/2").status_code == 404

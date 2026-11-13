"""Smoke test for an installed wheel: start the app and make one request of each kind."""

from __future__ import annotations

from bookshelf import create_app


def main() -> None:
    client = create_app().test_client()
    assert client.get("/health").get_json() == {"status": "ok", "books": 0}
    created = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "isbn": "0441172717", "year": 1965},
    )
    assert created.status_code == 201, created.get_data(as_text=True)
    assert client.get("/books").get_json()["count"] == 1
    print("smoke test passed")


if __name__ == "__main__":
    main()

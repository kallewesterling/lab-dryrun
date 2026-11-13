from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from flask.testing import FlaskClient

from bookshelf import BookStore, create_app

try:
    from hypothesis import settings
except ImportError:  # Hypothesis is a dev dependency; the property tests skip without it.
    pass
else:
    settings.register_profile("default", max_examples=100)
    settings.register_profile("ci", max_examples=2000, deadline=None)
    settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))

# Valid ISBN-13s used across the tests.
DUNE = "9780441172719"
NEUROMANCER = "9780441569595"
EARTHSEA = "9780547773742"


@pytest.fixture
def store() -> BookStore:
    return BookStore()


@pytest.fixture
def filled_store(store: BookStore) -> BookStore:
    store.add(title="Dune", author="Frank Herbert", isbn=DUNE, year=1965, tags=["sci-fi"])
    store.add(
        title="Neuromancer",
        author="William Gibson",
        isbn=NEUROMANCER,
        year=1984,
        tags=["sci-fi", "cyberpunk"],
    )
    store.add(
        title="A Wizard of Earthsea",
        author="Ursula K. Le Guin",
        isbn=EARTHSEA,
        year=1968,
        tags=["fantasy"],
    )
    return store


@pytest.fixture
def client(filled_store: BookStore) -> Iterator[FlaskClient]:
    app = create_app(filled_store)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

"""Run the API locally with `python -m bookshelf`."""

from bookshelf.app import create_app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8000)

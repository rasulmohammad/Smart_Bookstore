<img src="assets/icon.svg" width="64" height="64" alt="">

# Smart Bookstore

AI-enabled multimodal smart bookstore. A local Python desktop app (MVC) with
face and voice login, image search, a local RAG chat assistant, and JSON file
storage. No cloud services.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync          # create .venv and install dev tools
uv run pytest    # run tests
uv run ruff check .
```

Without uv: `python -m venv .venv && source .venv/bin/activate && pip install -e . pytest ruff`.

## Layout

| Path | Contents | Owner |
|---|---|---|
| `src/smart_bookstore/auth` | S1 Biometric auth and user management | Rasul |
| `src/smart_bookstore/catalog` | S2 Catalog search and recommendation | Thierno |
| `src/smart_bookstore/transactions` | S3 Transactions, deposits, finance | Dair |
| `src/smart_bookstore/moderation` | S4 Moderation and reviews | Bryant |
| `src/smart_bookstore/rag_inventory` | S5 RAG assistant and inventory | Rosina |
| `src/smart_bookstore/storage` | Shared JsonStore | all |
| `tests/` | Tests, one folder per package | all |
| `data/` | Local JSON data (not committed) | |
| `docs/design/` | Design diagrams and report notes | |

Each subsystem talks to another only through that subsystem's controller or
repository (see `docs/design/section1/1.1-overall-architecture.png`).

## Before you start coding

Check the open issues labeled
[`decision`](https://github.com/rasulmohammad/Smart_Bookstore/issues?q=is%3Aopen+label%3Adecision).
They block implementation: conflicting requirements (#4), stack choices (#5),
data file schemas (#6), and the creative feature (#7).

Add runtime libraries to `pyproject.toml` only when your subsystem needs them,
after #5 is settled.

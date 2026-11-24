import json

import pytest

from smart_bookstore.storage.json_store import JsonStore


def test_read_missing_file_returns_default(tmp_path):
    store = JsonStore(tmp_path)
    assert store.read("users", default=[]) == []


def test_write_then_read_round_trip(tmp_path):
    store = JsonStore(tmp_path)
    data = [{"id": "u1", "balance_cents": 500}]
    store.write("users", data)
    assert store.read("users") == data
    assert json.loads((tmp_path / "users.json").read_text()) == data


def test_write_creates_data_folder(tmp_path):
    store = JsonStore(tmp_path / "data")
    store.write("books", [])
    assert (tmp_path / "data" / "books.json").exists()


def test_failed_write_keeps_old_file_and_leaves_no_temp_file(tmp_path):
    store = JsonStore(tmp_path)
    store.write("users", [{"id": "u1"}])
    with pytest.raises(TypeError):
        store.write("users", [{"id": object()}])  # not JSON serializable
    assert store.read("users") == [{"id": "u1"}]
    assert [p.name for p in tmp_path.iterdir()] == ["users.json"]

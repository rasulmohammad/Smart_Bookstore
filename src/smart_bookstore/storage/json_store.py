"""Atomic JSON file storage shared by all repositories (design 1.1, Model layer)."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class JsonStore:
    """Reads and writes `<name>.json` files in one data folder.

    `write` saves to a temporary file and then renames it over the target,
    so a crash never leaves a half-written file.
    """

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)

    def _path(self, name: str) -> Path:
        return self.data_dir / f"{name}.json"

    def read(self, name: str, default: Any = None) -> Any:
        """Return the parsed contents of `<name>.json`, or `default` if it does not exist."""
        try:
            with self._path(name).open(encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return default

    def write(self, name: str, data: Any) -> None:
        """Replace `<name>.json` with `data` in one atomic step."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.data_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self._path(name))
        except BaseException:
            os.unlink(tmp)
            raise

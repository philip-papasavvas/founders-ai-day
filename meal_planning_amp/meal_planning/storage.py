"""Local data path helpers for the standalone meal planning app."""

from __future__ import annotations

from pathlib import Path


def resolve_data_file(filename: str) -> Path:
    """Resolve a data file from this standalone project.

    Resolution order:
    1. ``data/<filename>``
    2. ``_data/<filename>``

    If neither exists yet, return the writable ``data/<filename>`` location.
    """

    project_root = Path(__file__).resolve().parent.parent
    relative_path = Path(filename)
    for prefix in ("data", "_data"):
        candidate = project_root / prefix / relative_path
        if candidate.exists():
            return candidate
    return project_root / "data" / relative_path

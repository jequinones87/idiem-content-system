"""Shared pytest fixtures. Adds ``src/`` to the import path."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from idiem.loader import load_knowledge_base  # noqa: E402


@pytest.fixture(scope="session")
def kb():
    return load_knowledge_base()

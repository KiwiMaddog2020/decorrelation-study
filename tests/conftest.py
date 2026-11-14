"""Shared helpers. Tests read the repo but never write inside it: every output
goes to pytest's tmp_path."""
from __future__ import annotations
import importlib.util, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True


def load(relpath: str, name: str | None = None):
    """Load a repo script as a fresh module (fresh, so environment switches read
    at import time are picked up)."""
    path = ROOT / relpath
    name = name or "t_" + path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

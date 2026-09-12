"""
Condition registry — auto-discovers and loads all condition modules
in this directory that subclass Condition.
"""

import importlib
import pkgutil
from pathlib import Path
from .base import Condition

# Registry of all discovered conditions
_conditions: list[Condition] = []


def _discover_conditions():
    """Walk this package directory and instantiate every Condition subclass."""
    global _conditions
    _conditions = []

    package_dir = Path(__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name in ("base", "__init__"):
            continue
        module = importlib.import_module(f".{module_name}", package=__package__)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Condition)
                and attr is not Condition
            ):
                _conditions.append(attr())


def get_all_conditions() -> list[Condition]:
    """Return all registered condition instances."""
    if not _conditions:
        _discover_conditions()
    return _conditions


def reload_conditions():
    """Force re-discovery (useful after adding a new condition module)."""
    _discover_conditions()

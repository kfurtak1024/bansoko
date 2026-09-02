"""Import every module, so a broken import cannot reach a release.

Pyxel can be imported without a display; only pyxel.init() needs one. That
makes this cheap enough to run everywhere, and it is what catches an API
that vanished in a dependency upgrade.
"""
import importlib
import pkgutil

import pytest

import bansoko
import resbuilder


def _module_names() -> list[str]:
    names = []
    for package in (bansoko, resbuilder):
        for info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            # __main__ modules execute argument parsing on import.
            if not info.name.endswith("__main__"):
                names.append(info.name)
    return sorted(names)


@pytest.mark.parametrize("module_name", _module_names())
def test_module_imports(module_name: str) -> None:
    """Every module must import cleanly."""
    importlib.import_module(module_name)

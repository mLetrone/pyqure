"""Pyqure is a dependency injector.

It's inspired by the simplicity and magic of Spring annotations, to bring it to the python world.
"""

from importlib.metadata import PackageNotFoundError, version

from pyqure.injectables import Constant, qualifier
from pyqure.injection import component, configuration, create_injectable, factory, inject

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed or dist-info deleted
    __version__ = "undefined"


__all__ = [
    "Constant",
    "component",
    "configuration",
    "create_injectable",
    "factory",
    "inject",
    "qualifier",
]

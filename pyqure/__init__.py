"""Pyqure is a dependency injector.

It's inspired by the simplicity and magic of spring annotation, to bring it to the python world.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "undefined"

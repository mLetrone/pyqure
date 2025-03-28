"""Top level Pyqure package.

Pyqure is a dependency injector, inspired by the simplicity and magic of spring annotation.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "undefined"

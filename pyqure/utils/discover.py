import importlib
import inspect
import pkgutil

from pyqure.logger import logger


def discover(package_name: str | None = None) -> None:
    """Discover recursively all psub-package to perform auto-loading of modules, and so the injectables defined.

    If the package is provided, the discovering will be performed from it as root.
    Otherwise, it will use the package where the function is being called.
    """
    package_to_discover = package_name

    if package_to_discover is None:
        package_to_discover = _get_package_caller(2)

    if package_to_discover is None:
        raise ValueError("Should be call inside a package not a script.")

    package = importlib.import_module(package_to_discover)
    for _, module_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package_to_discover + "."
    ):
        if not is_pkg:
            imported_module = importlib.import_module(module_name)
            for name, _ in inspect.getmembers(imported_module):
                logger.debug(f"Add component {name} in {module_name}")


def _get_package_caller(lvl: int = 1) -> str | None:
    """Lookup the source package at the origin of a call.

    You should not have to use it outside the project.
    """
    frame = inspect.currentframe()
    for _ in range(lvl):
        if frame is None:
            return None

        frame = frame.f_back

    module = inspect.getmodule(frame)
    if module is None:
        return None

    return module.__package__

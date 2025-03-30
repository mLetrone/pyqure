from typing import Any, Callable, Iterable

from pyqure.utils.types import unpack_types


class PyqureError(Exception):
    """Pyqure general error."""


class DependencyError(PyqureError):
    """Dependency error."""


class InvalidRegisteredType(DependencyError):
    """Exception raised when invalid type used to register an injectable."""

    def __init__(self, type_: type[Any]) -> None:
        super().__init__(
            f"Union types cannot be used for registered injectables:"
            f" you provide {type_}, try registering separately one of {unpack_types(type_)}."
        )


class InjectionError(PyqureError):
    """Injection error."""


class MissingDependencies(InjectionError):
    """Missing dependency for service injection call."""

    def __init__(self, component: Callable[..., Any], missing: Iterable[str]) -> None:
        super().__init__(
            f"Cannot instantiate component {component}."
            f" Missed binding for the following parameters: {', '.join(missing)}."
        )
        self.component = component
        self.missing = missing

from typing import Any, Callable, Iterable

from pyqure.utils.types import unpack_types


class PyqureError(Exception):
    """Pyqure general error."""


class DependencyError(PyqureError):
    """Dependency error."""


class RegisterError(DependencyError):
    """Dependency error occurred during injectable registering."""


class NoUniqueInjectableError(RegisterError):
    """Injectable."""

    def __init__(self, clazz: type[Any] | None, alias: str | None) -> None:
        key_message = ""

        if clazz:
            key_message += f"with type <{clazz}>"

        if alias:
            key_message += f"{'and' if key_message else 'with'} qualifier <{alias}>"
        super().__init__(
            f"Error registering injectable {key_message}."
            " Another injectable is already register for this key,"
            " try using a qualifier or change it to a unique one."
        )


class InvalidRegisteredTypeError(RegisterError):
    """Exception raised when invalid type used to register an injectable."""

    def __init__(self, type_: type[Any]) -> None:
        super().__init__(
            f"Union types cannot be used for registered injectables:"
            f" you provide {type_}, try registering separately one of {unpack_types(type_)}."
        )


class InjectionError(PyqureError):
    """Injection error."""


class MissingDependenciesError(InjectionError):
    """Missing dependency for service injection call."""

    def __init__(self, component: Callable[..., Any], missing: Iterable[str]) -> None:
        super().__init__(
            f"Cannot instantiate component {component}."
            f" Missed binding for the following parameters: {', '.join(missing)}."
        )
        self.component = component
        self.missing = missing

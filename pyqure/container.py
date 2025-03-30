from contextlib import contextmanager
from logging import Logger
from pathlib import Path
from typing import Any, Generic, Iterator, NamedTuple, TypeVar

from typing_extensions import Self

from pyqure.exceptions import DependencyError, InvalidRegisteredType
from pyqure.injectables import Injectable
from pyqure.utils.types import filter_mro, is_union

logger = Logger("pyqure")

T = TypeVar("T")

DEFAULT_DEPENDENCIES_STATE_FILE = Path(".dependencies.pyq")


class Key(NamedTuple, Generic[T]):
    """Injectable key object."""

    clazz: type[T] | None
    qualifier: str | None


def Class(clz: type[T]) -> Key[T]:
    """Create a key with no qualifier."""
    return Key(clz, None)


def Alias(qualifier: str) -> Key[T]:
    """Create a key with no type."""
    return Key(None, qualifier)


class DependencyContainer:
    """Container of the whole dependency tree registered."""

    def __init__(
        self,
    ) -> None:
        self._primary: dict[type[Any], Key[Any]] = {}
        self._injectables: dict[Key[Any], Injectable[Any]] = {}
        self._overrides: dict[Key[Any], Injectable[Any]] = {}

    def register(self, key: Key[T], component: Injectable[T], *, primary: bool = False) -> Self:
        """Register a new injectable among the dependencies.

        Notes:
            Can add some options to the injectable registering impossible with __setitem__
                * primary : specify that to use the injectable for a class over others.

        Examples:
            >>> container.register(Key(int, "42"), Constant(42), primary=True).register(Key(int, "72"), Constant(72))
            >>> assert container[Class(int)] == 42
        """
        self.__register(key, component, primary)

        return self

    def __setitem__(self, key: Key[T], value: Injectable[T]) -> None:
        """Register a new injectable among the dependencies.

        Examples:
            >>> container[Key(int, "test")] = Constant(42)
            >>> assert container[Key(int, "test")] == 42
        """
        self.__register(key, value)

    def __getitem__(self, key: Key[T]) -> T:
        """Retrieve injectable by its Key.

        The injectable look up order:
            * Check if has been overridden
            * Check if the key exists inside dependencies
            * Check if an injectable has been set as primary for this type
            * Raise error
        """
        clss, qualifier = key
        if key in self._overrides:
            return self._overrides[key].supply()  # type: ignore[no-any-return]

        if key in self._injectables:
            return self._injectables[key].supply()  # type: ignore[no-any-return]

        if clss in self._primary:
            return self._injectables[self._primary[clss]].supply()  # type: ignore[no-any-return]

        raise DependencyError(f"No component found based on key: {key}.")

    def __contains__(self, key: Key[Any]) -> bool:
        """Check whether an injectable exists for this key."""
        clss, qualifier = key
        return clss in self._primary or key in self._injectables or key in self._overrides

    @contextmanager
    def override(self, key: Key[T], component: Injectable[T]) -> Iterator[None]:
        """Override a certain key with component within the context."""
        self._overrides[key] = component
        try:
            yield
        finally:
            del self._overrides[key]

    def __register(self, key: Key[T], component: Injectable[T], primary: bool = False) -> None:
        """Intern method registering an injectable."""
        clzz, qualifier = key

        if clzz:
            if is_union(clzz):
                raise InvalidRegisteredType(clzz)

            for cls in filter_mro(clzz):
                self._injectables[Key(cls, qualifier)] = component
                if primary:
                    self._primary[cls] = key
        else:
            self._injectables[key] = component


dc: DependencyContainer = DependencyContainer()

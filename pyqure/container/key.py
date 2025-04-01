from typing import Any, Generic, NamedTuple, TypeVar

T = TypeVar("T")


class Key(NamedTuple, Generic[T]):
    """Injectable key object."""

    clazz: type[T] | None
    qualifier: str | None


def Class(clz: type[T]) -> Key[T]:
    """Create a key with no qualifier."""
    return Key(clz, None)


def Alias(qualifier: str) -> Key[Any]:
    """Create a key with no type."""
    return Key(None, qualifier)

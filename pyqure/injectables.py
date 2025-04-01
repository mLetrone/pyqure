from dataclasses import dataclass, field
from typing import Callable, Protocol, TypeVar

from typing_extensions import override

T = TypeVar("T", covariant=True)


class Qualifier(str):
    """Marker to specify alias for injectable."""


def qualifier(alias: str) -> Qualifier:
    """Create a qualifier alias to specify which component to inject.

    Examples:
        ```python
        @inject
        def my_function(service: Annotated[Service, qualifier("alias")]) -> None:
            ...
        ```
    """
    return Qualifier(alias)


class Injectable(Protocol[T]):
    """Injectable object contract."""

    def supply(self) -> T:
        """Supply the injectable component/value."""


@dataclass(slots=True)
class Constant(Injectable[T]):
    """Component to create Injectable constant.

    Examples:
        >>> container[Key(str, "contract_table_name")] = Constant("Contract")
    """

    value: T

    @override
    def supply(self) -> T:
        return self.value


@dataclass(slots=True)
class Singleton(Injectable[T]):
    """Singleton injectable.

    Singleton is lazy evaluated by design, the component is only instantiated
    when needed.
    """

    supplier: Callable[..., T]
    value: T | None = field(init=False, default=None)

    @override
    def supply(self) -> T:
        if self.value is None:
            self.value = self.supplier()

        return self.value


@dataclass(slots=True)
class Factory(Injectable[T]):
    """Factory injectable.

    Each time the injectable is needed, a new instance is created.
    """

    supplier: Callable[..., T]

    @override
    def supply(self) -> T:
        return self.supplier()

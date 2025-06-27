from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Union

import pytest

from pyqure import component, factory
from pyqure.container import Alias, Class, DependencyContainer, Key
from pyqure.exceptions import DependencyError, InvalidRegisteredTypeError, NoUniqueInjectableError
from pyqure.injectables import Constant
from tests.fixtures.abstracts import ABCService, ConcreteService


class TestContainer:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.container = DependencyContainer()

    def test_register(self) -> None:
        self.container.register(Key(int, "test"), Constant(42))

        assert self.container[Key(int, "test")] == 42

    def test_register_with_only_alias(self) -> None:
        self.container.register(Alias("test"), Constant(42))

        assert self.container[Alias("test")] == 42

    def test_register_with_only_type(self) -> None:
        self.container.register(Class(int), Constant(42))

        assert self.container[Class(int)] == 42

    def test_register_should_register_all_super_classes_of_type(self) -> None:
        service = ConcreteService()

        self.container.register(Key(ConcreteService, "test"), Constant(service))

        assert self.container[Key(ConcreteService, "test")] == service
        assert self.container[Key(ABCService, "test")] == service

    def test_register_with_generics_types(self) -> None:
        self.container.register(Key(dict[str, int], "test"), Constant({"count": 0}))

        assert self.container[Key(dict[str, int], "test")] == {"count": 0}
        assert self.container[Key(dict, "test")] == {"count": 0}

    @pytest.mark.parametrize("union", [Union[str | int], Optional[dict[str, int]], str | Path])
    def test_register_raises_when_using_union_types(self, union: type[Any]) -> None:
        with pytest.raises(InvalidRegisteredTypeError):
            self.container[Class(union)] = Constant("error")

    def test_register_with_primary(self) -> None:
        self.container.register(Key(int, "test"), Constant(42), primary=True)

        assert self.container[Class(int)] == 42
        assert self.container[Key(int, "test")] == 42

    def test_get_no_result_should_raise_error(self) -> None:
        with pytest.raises(DependencyError):
            _a = self.container[Key(int, "test")]

    def test_get_when_no_primary(self) -> None:
        self.container.register(Key(int, "42"), Constant(42)).register(Key(int, "72"), Constant(72))

        assert self.container[Key(int, "72")] == 72

    def test_get_raises_when_multiple_injectables_same_type_and_no_primary_class_key(self) -> None:
        self.container.register(Key(int, "42"), Constant(42)).register(Key(int, "72"), Constant(72))

        with pytest.raises(DependencyError):
            _a = self.container[Class(int)]

    def test_collision(self) -> None:
        with pytest.raises(NoUniqueInjectableError):

            class Service(ABC):
                @abstractmethod
                def execute(self) -> str: ...

            @component(container=self.container)
            class PostgresService(Service):
                def execute(self) -> str:
                    return "PostgresService"

            @factory(container=self.container)
            class InMemoryService(Service):
                def execute(self) -> str:
                    return "InMemoryService"

            self.container[Class(Service)]  # type: ignore[type-abstract]

    def test_get_when_primary(self) -> None:
        self.container.register(Key(int, "42"), Constant(42)).register(
            Key(int, "72"), Constant(72), primary=True
        ).register(Key(int, "0"), Constant(0))

        assert self.container[Class(int)] == 72

    def test_override(self) -> None:
        self.container[Key(int, "test")] = Constant(42)

        with self.container.override(Key(int, "test"), Constant(0)):
            assert self.container[Key(int, "test")] == 0

        assert self.container[Key(int, "test")] == 42

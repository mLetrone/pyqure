from pathlib import Path
from typing import Any, Optional, Union

import pytest

from pyqure.container import Alias, Class, DependencyContainer, Key
from pyqure.exceptions import DependencyError, InvalidRegisteredType
from pyqure.injectables import Constant
from tests.fixtures.abstracts import ABCService, ConcreteService


class TestContainer:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.container = DependencyContainer()

    def test_register(self) -> None:
        self.container.register(Key(int, "test"), Constant(42))

        assert self.container._overrides == {}
        assert self.container._primary == {}
        assert self.container._injectables == {(int, "test"): Constant(42)}

    def test_register_with_only_alias(self) -> None:
        self.container.register(Alias("test"), Constant(42))

        assert self.container._overrides == {}
        assert self.container._primary == {}
        assert self.container._injectables == {(None, "test"): Constant(42)}

    def test_register_with_only_type(self) -> None:
        self.container.register(Class(int), Constant(42))

        assert self.container._overrides == {}
        assert self.container._primary == {}
        assert self.container._injectables == {(int, None): Constant(42)}

    def test_register_should_register_all_super_classes_of_type(self) -> None:
        constant = Constant(ConcreteService())
        self.container.register(Key(ConcreteService, "test"), constant)

        assert self.container._overrides == {}
        assert self.container._primary == {}
        assert self.container._injectables == {
            (ConcreteService, "test"): constant,
            (ABCService, "test"): constant,
        }

    def test_register_with_generics_types(self) -> None:
        self.container.register(Key(dict[str, int], "test"), Constant({"count": 0}))

        assert self.container._overrides == {}
        assert self.container._primary == {}
        assert self.container._injectables == {
            (dict[str, int], "test"): Constant({"count": 0}),
            (dict, "test"): Constant({"count": 0}),
        }

    @pytest.mark.parametrize("union", [Union[str | int], Optional[dict[str, int]], str | Path])
    def test_register_raises_when_using_union_types(self, union: type[Any]) -> None:
        with pytest.raises(InvalidRegisteredType):
            self.container[Class(union)] = Constant("error")

    def test_register_with_primary(self) -> None:
        self.container.register(Key(int, "test"), Constant(42), primary=True)

        assert len(self.container._overrides) == 0
        assert self.container._primary == {int: (int, "test")}
        assert self.container._injectables == {(int, "test"): Constant(42)}

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

    def test_get_when_primary(self) -> None:
        self.container.register(Key(int, "42"), Constant(42)).register(
            Key(int, "72"), Constant(72), primary=True
        ).register(Key(int, "0"), Constant(0))

        assert self.container[Class(int)] == 72

    def test_override(self) -> None:
        self.container[Key(int, "test")] = Constant(42)

        with self.container.override(Key(int, "test"), Constant(0)):
            assert self.container[Key(int, "test")] == 0

        assert self.container._overrides == {}
        assert self.container[Key(int, "test")] == 42

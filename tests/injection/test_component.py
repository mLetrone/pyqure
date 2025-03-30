import pytest

from pyqure.container import Alias, Class, DependencyContainer, Key
from pyqure.exceptions import InjectionError
from pyqure.injection import component
from tests.fixtures.abstracts import ABCService, HasA


class TestComponent:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        # use container to isolate tests run.
        self.container = DependencyContainer()

    @pytest.mark.parametrize("clazz", [ABCService, HasA])
    def test_raise_error_on_abstract_classes(self, clazz: type) -> None:
        with pytest.raises(
            InjectionError, match="impossible to instantiate abstract or protocol classes"
        ):
            component(clazz)

    def test_on_class(self) -> None:
        @component(container=self.container)
        class Service: ...

        comp = self.container[Class(Service)]

        assert isinstance(Service(), Service)
        assert isinstance(comp, Service)

        assert comp is self.container[Class(Service)]

    def test_on_class_with_inheritance(self) -> None:
        @component(container=self.container)
        class MyService(ABCService):
            def method(self) -> None: ...

        comp = self.container[Class(MyService)]
        # https://github.com/python/mypy/issues/4717#issuecomment-1261038011
        comp_parent = self.container[Class(ABCService)]  # type: ignore[type-abstract]

        assert isinstance(MyService(), MyService)
        assert isinstance(comp, MyService)
        assert comp is comp_parent

    def test_on_class_with_qualifier(self) -> None:
        @component(qualifier="custom", container=self.container)
        class MyService(ABCService):
            def method(self) -> None: ...

        comp = self.container[Key(MyService, "custom")]
        comp_parent = self.container[Key(ABCService, "custom")]

        assert isinstance(MyService(), MyService)
        assert isinstance(comp, MyService)

        assert comp is comp_parent

    def test_on_function(self) -> None:
        @component(container=self.container)
        def service():  # type: ignore[no-untyped-def]
            return "Hello"

        comp: str = self.container[Alias("service")]

        assert isinstance(comp, str)

        assert comp is self.container[Alias("service")]
        assert comp == "Hello"

    def test_on_typed_function(self) -> None:
        @component(container=self.container)
        def service() -> str:
            return "Hello"

        comp = self.container[Key(str, "service")]

        assert comp == "Hello"

    def test_on_function_with_qualifier(self) -> None:
        @component(qualifier="hello", container=self.container)
        def service() -> str:
            return "Hello"

        comp = self.container[Key(str, "hello")]

        assert comp == "Hello"

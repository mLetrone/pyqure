import pytest

from pyqure.container import Alias, Class, DependencyContainer, Key
from pyqure.exceptions import DependencyError, InjectionError
from pyqure.injection import factory
from tests.fixtures.abstracts import ABCService, HasA


class TestFactory:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        # use container to isolate tests run.
        self.container = DependencyContainer()

    @pytest.mark.parametrize("clazz", [ABCService, HasA])
    def test_raise_error_on_abstract_classes(self, clazz: type) -> None:
        with pytest.raises(
            InjectionError, match="impossible to instantiate abstract or protocol classes"
        ):
            factory(clazz)

    def test_on_class(self) -> None:
        @factory(container=self.container)
        class Service: ...

        comp = self.container[Class(Service)]

        assert isinstance(Service(), Service)
        assert isinstance(comp, Service)

        assert id(comp) != id(self.container[Class(Service)])

    def test_on_class_with_inheritance(self) -> None:
        @factory(container=self.container)
        class MyService(ABCService):
            def method(self) -> None: ...

        comp = self.container[Class(MyService)]
        # # https://github.com/python/mypy/issues/4717#issuecomment-1261038011
        comp_parent = self.container[Class(ABCService)]  # type: ignore[type-abstract]

        assert isinstance(MyService(), MyService)
        assert isinstance(comp, MyService)
        assert id(comp) != id(comp_parent)

    def test_on_class_with_qualifier(self) -> None:
        @factory(qualifier="custom", container=self.container)
        class MyService(ABCService):
            def method(self) -> None: ...

        comp = self.container[Key(MyService, "custom")]
        comp_parent = self.container[Key(ABCService, "custom")]

        assert isinstance(MyService(), MyService)
        assert isinstance(comp, MyService)

        assert id(comp) != id(comp_parent)

    def test_on_function(self) -> None:
        @factory(container=self.container)
        def service():  # type: ignore[no-untyped-def]
            return {"en": "Hello", "fr": "Bonjour"}

        comp: dict[str, str] = self.container[Alias("service")]

        assert isinstance(comp, dict)

        assert id(comp) != id(self.container[Alias("service")])
        assert comp == {"en": "Hello", "fr": "Bonjour"}

    def test_on_typed_function(self) -> None:
        @factory(container=self.container)
        def service() -> dict[str, str]:
            return {"en": "Hello", "fr": "Bonjour"}

        comp = self.container[Key(dict[str, str], "service")]
        comp_sub_type = self.container[Key(dict, "service")]

        assert id(comp) != id(self.container[Key(dict[str, str], "service")])
        assert comp == comp_sub_type == {"en": "Hello", "fr": "Bonjour"}

    def test_on_function_with_qualifier(self) -> None:
        @factory(qualifier="hello", container=self.container)
        def service() -> dict[str, str]:
            return {"en": "Hello", "fr": "Bonjour"}

        comp = self.container[Key(dict[str, str], "hello")]

        assert comp == {"en": "Hello", "fr": "Bonjour"}

        with pytest.raises(DependencyError):
            _a = self.container[Key(dict[str, str], "service")]

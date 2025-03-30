import pytest

from pyqure.container import Alias, DependencyContainer, Key
from pyqure.injectables import Constant
from pyqure.injection import configuration


class TestConfiguration:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.container = DependencyContainer()

    def test_register_components(self) -> None:
        @configuration(container=self.container)
        def configs(container: DependencyContainer) -> None:
            container[Alias("42")] = Constant(42)
            container[Key(dict[str, str], "hello")] = Constant({"en": "Hello", "fr": "Bonjour"})

        assert self.container[Alias("42")] == 42
        assert self.container[Key(dict[str, str], "hello")] == {"en": "Hello", "fr": "Bonjour"}

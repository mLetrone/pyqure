from abc import ABC, abstractmethod
from pathlib import Path
from typing import Annotated

import pytest

from pyqure.container import Class, DependencyContainer, Key
from pyqure.exceptions import MissingDependencies
from pyqure.injectables import Constant, qualifier
from pyqure.injection import component, configuration, inject


class TestInject:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.container = DependencyContainer()

    def test_raise_error_when_missing_injectable(self) -> None:
        @inject(container=self.container)
        def run(data: dict[str, str]) -> None:
            pass

        with pytest.raises(
            MissingDependencies, match="Missed binding for the following parameters: data."
        ):
            run()

    def test_with_component(self) -> None:
        @inject(container=self.container)
        def run(data: dict[str, str]) -> dict[str, str]:
            return data

        assert run({"es": "Hola"}) == {"es": "Hola"}
        assert run(data={"es": "Hola"}) == {"es": "Hola"}

        @component(container=self.container)
        def data() -> dict[str, str]:
            return {"en": "Hello", "fr": "Bonjour"}

        assert run() == {"en": "Hello", "fr": "Bonjour"}

    def test_without_types(self) -> None:
        @inject(container=self.container)
        def run(data):  # type: ignore[no-untyped-def]
            return data

        @component(container=self.container)
        def data():  # type: ignore[no-untyped-def]
            return {"en": "Hello", "es": "Hola"}

        assert run() == {"en": "Hello", "es": "Hola"}

    def test_multiples_injectables(self) -> None:
        @inject(container=self.container)
        def run(a: int, b: int) -> int:
            return a * b

        @configuration(container=self.container)
        def configs(container: DependencyContainer) -> None:
            container[Key(int, "a")] = Constant(2)
            container[Key(int, "b")] = Constant(4)

        assert run() == 8

    def test_with_default_value(self) -> None:
        @inject(container=self.container)
        def run(a: int, b: int, c: int = 1) -> int:
            return a * b - c

        @configuration(container=self.container)
        def configs(container: DependencyContainer) -> None:
            container[Key(int, "a")] = Constant(2)
            container[Key(int, "b")] = Constant(4)

        assert run() == 7

        @component(qualifier="c", container=self.container)
        def minus() -> int:
            return 7

        assert run() == 1

    def test_with_union_types(self) -> None:
        @configuration(container=self.container)
        def config(container: DependencyContainer) -> None:
            container[Key(Path, "path")] = Constant(Path("test_path"))

        @inject(container=self.container)
        def run(path: str | Path) -> str:
            return Path(path).name

        assert run() == "test_path"

    def test_complete_inline(self) -> None:
        @component
        class HttpClient:
            def __repr__(self) -> str:
                return "HttpClient"

        class Service(ABC):
            @abstractmethod
            def print(self) -> str: ...

        class Name:
            def __init__(self, name: str) -> None:
                self.name = name

            def __repr__(self) -> str:
                return self.name

        @component(qualifier="unicorn")
        class ServiceUnicorn(Service):
            def __init__(self, http_client: HttpClient, name: str | Name) -> None:
                self.http_client = http_client
                self.name = name

            def print(self) -> str:
                return f"{self.name} unicorn"

            def __repr__(self) -> str:
                return f"ServiceUnicorn({self.http_client=}, {self.name=})"

        @component(qualifier="tiger")
        class ServiceTiger(Service):
            def __init__(self, http_client: HttpClient) -> None:
                self.http_client = http_client

            def print(self) -> str:
                return "tiger"

            def __repr__(self) -> str:
                return f"ServiceTiger({self.http_client=})"

        @configuration
        def config(container: DependencyContainer) -> None:
            container[Class(Name)] = Constant(Name("rainbow"))

        @inject
        def run(service: Annotated[Service, qualifier("unicorn")]) -> str:
            print(service)
            return service.print()

        assert run() == "rainbow unicorn"

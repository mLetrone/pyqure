# Pyqure

_Unlock seamless dependency injection with the effortless charm of Spring annotations_

<div align="center" style="margin:40px;">
<!-- --8<-- [start:overview-header] -->

[![Test](https://github.com/MLetrone/pyqure/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MLetrone/pyqure/actions/workflows/ci.yml)
[![Coverage](https://raw.githubusercontent.com/mLetrone/pyqure/_xml_coverage_reports/data/main/badge.svg)](https://raw.githubusercontent.com/mLetrone/pyqure/_xml_coverage_reports/data/main/coverage.xml)
[![Language](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FmLetrone%2Fpyqure%2Fmain%2Fpyproject.toml)](https://www.python.org/)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Style](https://img.shields.io/badge/Style-ruff-9a9a9a?style=flat-square)
![Lint](https://img.shields.io/badge/Lint-ruff,%20mypy-brightgreen?style=flat-square)

<!-- --8<-- [end:overview-header] -->

---

Source Code: [https://github.com/MLetrone/pyqure](https://github.com/MLetrone/pyqure)

---
</div>
<!-- --8<-- [start:overview-body] -->

## Description

**Pyqure** is a dependency injector, that brings the simplicity of Spring annotations to the Python world.
It will inject your different dependency either based on parameters name (feel like pytest fixture injection)
or/and standard Python types hints.

No more manual description of all your dependency management,
all you need is some decorators to register them and inject them.

[//]: # (TODO explain dependency injection ?)

## Key features

* **API**: Simple, easy to use and learn.
* **Short**: Go to the essential, no settings file or boilerplate code.
* **Lightweight**: Light as a feather.

## Installation

To install Pyqure, you can use the package manager of your choice, here an example with pip:

```bash
pip install pyqure
```

## Usage

Two essential actions, registering dependencies (injectable), and retrieving them for injection.

### Registering

Using decorators to register injectables from classes or functions.
You can choose between two kinds of injectables:

- Singleton: using `@component`
    - Once instantiated, the same object will be injected each time
- Factory: using `@factory`
    - Each time a new instance will be injected

#### Classes

It will register the class and all parents classes, with the injectable.
You can optionally provide a qualifier to differentiate it from other component of the same type.

```python
from abc import ABC, abstractmethod

from pyqure import component, factory


class Service(ABC):
    @abstractmethod
    def execute(self) -> str: ...


@component
class PostgresService(Service):
    def execute(self) -> str:
        return "PostgresService"


@factory(qualifier="in_memory_service")
class InMemoryService(Service):
    def execute(self) -> str:
        return "InMemoryService"
```

#### Functions

Almost the same with function, except depends on your choice,
you can add type hints (highly recommended) or not.
Therefore, if the function is typed, it will be registered by its name and its return type.

##### Without type hints

```python
from pyqure import component


@component
def data():
    return {"en": "Hello", "es": "Hola"}

```

##### With type hints

```python
from pyqure import component


@component
def data() -> dict[str, str]:
    return {"en": "Hello", "es": "Hola"}
```

### Injecting

Use the `@inject` decorator to define an injection entrypoint.
The decorated function can either be called with all its arguments or partially.
In case of partially call, Pyqure will resolve the dependencies to inject based on parameters name and types.
This operation is performed through all the dependencies branches needed by the injection.

Pyqure resolves dependencies with the following order:

1. By name (for untyped parameters).
2. By name and type
3. By qualifier (if provider via `Annotated`) and type.
4. Fallback to default parameter value if available
5. Raise error for missing arguments.

Concerning type lookup, feel free to use union type, Pyqure handle them ;)

```python
from typing import Annotated

from pyqure import inject, qualifier


@inject
def main(service: Annotated[Service, qualifier("in_memory_service")], data: dict[str, str]) -> None:
    print(f"{data['en']} {service.execute()}")


main()
>>> "Hello InMemoryService"
```

---
**N.B**
Due to the nature of Python (interpreted), when executing an inject function,
the program may not yet have loaded your modules where the registration is performed.
To counter, that you can either use `@configuration` decorator flagging at autoload or `discover`.

They will load all the project modules, it's more convenient to do it in the `__init__.py` at the top of your application.

### Examples

A complete example with a multi-packages project can be found on [`tests/examples`](https://github.com/mLetrone/pyqure/tree/main/tests/examples).

Here's an advance example with multi-dependencies injectables:

```python
from abc import ABC, abstractmethod
from typing import Annotated

from pyqure import Constant, component, configuration, inject, qualifier
from pyqure.container import Class, DependencyContainer


@component
class HttpClient:
    def __repr__(self) -> str:
        return "HttpClient"


class Printer(ABC):
    @abstractmethod
    def print(self) -> str: ...


class Name(str):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


@component(qualifier="unicorn")
class UnicornPrinter(Printer):
    def __init__(self, http_client: HttpClient, name: str | Name) -> None:
        self.http_client = http_client
        self.name = name

    def print(self) -> str:
        return f"{self.name} unicorn"

    def __repr__(self) -> str:
        return f"UnicornPrinter({self.http_client=}, {self.name=})"


@component(qualifier="tiger")
class TigerPrinter(Printer):
    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    def print(self) -> str:
        return "tiger"

    def __repr__(self) -> str:
        return f"TigerPrinter({self.http_client=})"


@configuration
def config(container: DependencyContainer) -> None:
    container[Class(Name)] = Constant(Name("rainbow"))


@inject
def run(service: Annotated[Printer, qualifier("unicorn")]) -> str:
    print(service)
    return service.print()


assert run() == "rainbow unicorn"
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

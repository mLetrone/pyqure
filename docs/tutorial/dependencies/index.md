**Pyqure** perform dependency injection using the **Injectable**s,
which are dependencies that **Pyqure** can manipulate,
by instantiating or injecting them to instantiate others injectables.

All you have to do is to register them, using decorators, it can be classes or functions.
There are two kinds of injectables registrable through decorators:

how to bake as an ordered list:

<div class="annotate" markdown>
- Singleton: with `@component` (1).
- Factory: with `@factory` (2)
</div>

1.  Once instantiated, the same object will be injected each time.
2.  Each time a new instance is injected.

!!! tip
    Both are lazy, they will be instantiated **only** if there are needed ;)

## Classes

It will register the class and all parents classes, with the injectable.
You can optionally provide a qualifier to differentiate it from others injectables.
It's also possible to

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


@factory(qualifier="in-memory")
class InMemoryService(Service):
    def execute(self) -> str:
        return "InMemoryService"
```

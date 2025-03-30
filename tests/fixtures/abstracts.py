from abc import ABC, abstractmethod
from typing import Protocol


class ABCService(ABC):
    @abstractmethod
    def method(self) -> None: ...


class ConcreteService(ABCService):
    def method(self) -> None:
        return None


class HasA(Protocol):
    a: int


class HasAAndB(HasA):
    a: int
    b: int

from pathlib import Path

from pyqure.injectables import Constant, Factory, Singleton


def test_constant() -> None:
    constant = Constant("constant")

    supplieds = [constant.supply() for _ in range(5)]

    assert all(supplied == "constant" for supplied in supplieds)


def test_singleton() -> None:
    singleton = Singleton(lambda: Path(".singleton"))

    value = singleton.supply()
    createds = [singleton.supply() for _ in range(5)]

    assert all(created is value for created in createds)


def test_factory() -> None:
    factory = Factory(lambda: Path(".factory"))

    value = factory.supply()
    createds = [factory.supply() for _ in range(5)]

    assert all(created == value and created is not value for created in createds)

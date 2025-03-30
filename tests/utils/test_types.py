from inspect import Parameter
from os import PathLike
from pathlib import Path
from typing import Annotated, Any, Optional, Union

import pytest

from pyqure.injectables import Qualifier, qualifier
from pyqure.utils.types import (
    extract_type_info,
    filter_mro,
    has_parameter_type,
    is_annotated,
    is_interface,
    is_optional,
    is_union,
    unpack_types,
)
from tests.fixtures.abstracts import ABCService, ConcreteService, HasA, HasAAndB


@pytest.mark.parametrize(
    ("t", "expected"),
    [
        (int, (int,)),
        (Optional[str], (str,)),
        (None | str, (str,)),
        (dict[str, str] | None, (dict[str, str],)),
        (str | PathLike | Path, (str, PathLike, Path)),
        (Annotated[int | str, "metadata"], (int, str)),
    ],
)
def test_unpack_types(t: type, expected: tuple[type, ...]) -> None:
    assert unpack_types(t) == expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [(ABCService, True), (ConcreteService, False), (HasA, True), (HasAAndB, False)],
)
def test_is_interface(type_: type, expected: bool) -> None:
    assert is_interface(type_) is expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [(Union[str, int], True), (str | int, True), (int, False), (dict[str, str], False)],
)
def test_is_union(type_: type, expected: bool) -> None:
    assert is_union(type_) is expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [(Optional[str], True), (dict[str, int] | None, True), (None | str, True), (int, False)],
)
def test_is_optional(type_: type, expected: bool) -> None:
    assert is_optional(type_) is expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [(Optional[str], False), (Annotated[int | str, "metadata"], True), (str, False)],
)
def test_is_annotated(type_: type, expected: bool) -> None:
    assert is_annotated(type_) is expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [(Any, True), (dict[str, int] | None, True), (None | str, True), (Parameter.empty, False)],
)
def test_has_parameter_type(type_: type, expected: bool) -> None:
    assert has_parameter_type(type_) is expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, [int]),
        (
            dict[str, int],
            [
                dict[str, int],
                dict,
            ],
        ),
        (ConcreteService, [ConcreteService, ABCService]),
    ],
)
def test_filter_mro(type_: type, expected: list[type]) -> None:
    assert filter_mro(type_) == expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, (int, None)),
        (dict[str, int], (dict[str, int], None)),
        (Annotated[ConcreteService, qualifier("test")], (ConcreteService, Qualifier("test"))),
    ],
)
def test_extract_type_info(type_: type, expected: tuple[type, Qualifier | None]) -> None:
    assert extract_type_info(type_) == expected

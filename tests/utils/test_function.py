from typing import Annotated

from pyqure.injectables import Qualifier, qualifier
from pyqure.utils.function import AnyType, NoDefault, Param, Parameters


class TestParameters:
    def test_get_function_parameters_without_types(self) -> None:
        def foo(a, /, b): ...  # type: ignore[no-untyped-def]

        params = Parameters(foo)

        assert params.value == {
            "a": Param(AnyType, True, "a", NoDefault, None),
            "b": Param(AnyType, False, "b", NoDefault, None),
        }

    def test_get_function_parameters_without_types_and_default(self) -> None:
        def foo(a, /, b="default"): ...  # type: ignore[no-untyped-def]

        params = Parameters(foo)

        assert params.value == {
            "a": Param(AnyType, True, "a", NoDefault, None),
            "b": Param(AnyType, False, "b", "default", None),
        }

    def test_get_function_parameters_with_types(self) -> None:
        def foo(a: int, /, b: str) -> int: ...  # type: ignore[empty-body]

        params = Parameters(foo)

        assert params.value == {
            "a": Param(int, True, "a", NoDefault, None),
            "b": Param(str, False, "b", NoDefault, None),
        }

    def test_get_function_parameters_with_types_and_default(self) -> None:
        def foo(a: int, /, b: str = "default") -> int:  # type: ignore[empty-body]
            pass

        params = Parameters(foo)

        assert params.value == {
            "a": Param(int, True, "a", NoDefault, None),
            "b": Param(str, False, "b", "default", None),
        }

    def test_get_function_parameters_with_forward_ref(self) -> None:
        def foo(a: int, /, b: "TestParameters") -> int: ...  # type: ignore[empty-body]

        params = Parameters(foo)

        assert params.value == {
            "a": Param(int, True, "a", NoDefault, None),
            "b": Param(TestParameters, False, "b", NoDefault, None),
        }

    def test_get_function_complete(self) -> None:
        def foo(  # type: ignore[empty-body]
            a: Annotated[int, "metadata"],
            /,
            b: Annotated["TestParameters", qualifier("test")],
            *,
            c: bool = True,
        ) -> int: ...

        params = Parameters(foo)

        assert params.value == {
            "a": Param(int, True, "a", NoDefault, None),
            "b": Param(TestParameters, False, "b", NoDefault, Qualifier("test")),
            "c": Param(bool, False, "c", True, None),
        }

    def test_at_position(self) -> None:
        def foo(a, b, c, d): ...  # type: ignore[no-untyped-def]

        params = Parameters(foo)

        assert params.at_position(2).name == "c"

    def test_missings(self) -> None:
        def foo(a, b, c, d="bar"): ...  # type: ignore[no-untyped-def]

        params = Parameters(foo)

        missings = params.missings([0], {"c": False})

        assert missings == {
            "b": Param(AnyType, False, "b", NoDefault, None),
            "d": Param(AnyType, False, "d", "bar", None),
        }

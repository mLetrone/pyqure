from abc import ABC
from inspect import Parameter, isabstract
from types import GenericAlias, NoneType, UnionType
from typing import Annotated, Protocol, Sequence, TypeGuard, Union, get_args, get_origin

from pyqure.injectables import Qualifier

_OPTIONAL_SIZE = 2


def unpack_types(typ: type) -> tuple[type, ...]:
    """Unpack types."""
    if not is_union(typ):
        if is_annotated(typ):
            return unpack_types(typ.__origin__)
        return (typ,)
    if not is_optional(typ):
        return get_args(typ)
    return (_get_optional_type(typ),)


def is_optional(typ: type) -> bool:
    """Check if it is optional type or not."""
    type_items = get_args(typ)
    return (
        is_union(typ)
        and len(type_items) == _OPTIONAL_SIZE
        and any(sub_type is NoneType for sub_type in type_items)
    )


def _get_optional_type(typ: type) -> type:
    type_items = get_args(typ)

    if type_items[0] is NoneType:
        return type_items[1]  # type: ignore[no-any-return]
    return type_items[0]  # type: ignore[no-any-return]


def is_union(typ: type) -> TypeGuard[type[Union]]:
    """Check whether the type is a union type or not."""
    return get_origin(typ) in (Union, UnionType)


def is_annotated(typ: type) -> TypeGuard[type[Annotated]]:  # type: ignore[valid-type]
    """Check whether the type is annotated or not."""
    return get_origin(typ) is Annotated


def is_interface(typ: type) -> bool:
    """Check whether class is an interface or not.

    If class inherits from `ABC` or `Protocol`, it's declared as interface class.
    """
    return isabstract(typ) or typ.__base__ in (ABC, Protocol)


def has_parameter_type(typ: type) -> bool:
    """Check whether the type is defined and not Parameter.empty."""
    return typ is not Parameter.empty


def filter_mro(clazz: type) -> Sequence[type]:
    """Get the mro of type filtered of ABC, object and Protocol hierarchy."""
    mro = [cls for cls in clazz.mro() if cls not in (ABC, object, Protocol)]
    if isinstance(clazz, GenericAlias):
        return [clazz, *mro]
    return mro


def extract_type_info(type_: type) -> tuple[type, Qualifier | None]:
    """You shouldn't use it directly outside the project.

    Extract type and qualifier if exists.
    """
    if is_annotated(type_):
        return (
            type_.__origin__,
            next(
                (qualifier for qualifier in get_args(type_) if isinstance(qualifier, Qualifier)),
                None,
            ),
        )
    return type_, None

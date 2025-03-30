import sys
from dataclasses import dataclass
from inspect import Parameter, Signature, signature
from typing import Annotated, Any, Callable, ForwardRef, Sequence

from pyqure.injectables import Qualifier
from pyqure.utils.types import extract_type_info, has_parameter_type

ParamName = Annotated[str, "Parameter name"]


class AnyType:
    """Used as a sentinel to define the parameter type when no type used in the signature."""


class NoDefault:
    """Used as a sentinel to define that the parameter has no default value."""


@dataclass(slots=True)
class Param:
    """Custom class modeling parameter."""

    type: type
    is_positional_only: bool
    name: str
    default: Any
    qualifier: Qualifier | None


class Parameters:
    """Utily class to parse and manupilate function signature."""

    def __init__(self, func: Callable[..., Any]) -> None:
        self.signature = signature(func)

        self._positional_names = tuple(self.signature.parameters.keys())
        self.value = self._get_parameters(self.signature, getattr(func, "__module__", None))

    @property
    def defaults(self) -> dict[ParamName, Param]:
        """Parameters with default value."""
        return {key: value for key, value in self.value.items() if value.default is not NoDefault}

    @property
    def mandatory(self) -> dict[ParamName, Param]:
        """Mandatory parameters, the parameters that do not have default value."""
        return {key: value for key, value in self.value.items() if value.default is NoDefault}

    def at_position(self, index: int) -> Param:
        """Get the parameter at position."""
        return self.value[self._positional_names[index]]

    def partial_bind(
        self, positionals: Sequence[Any], kwargs: dict[str, Any]
    ) -> dict[ParamName, Param]:
        """Gather the parameters partial passed to get the submitted."""
        return {self.at_position(pos).name: value for pos, value in enumerate(positionals)} | kwargs

    def missing(
        self, positionals: Sequence[Any] = (), kwargs: dict[ParamName, Any] | None = None
    ) -> dict[ParamName, Param]:
        """Returns missing parameters between the function signature and the provided."""
        submitting_parameters = self.partial_bind(positionals, kwargs or {})

        return {key: value for key, value in self.value.items() if key not in submitting_parameters}

    def _get_parameters(self, sig: Signature, func_module: str | None) -> dict[ParamName, Param]:
        """Extract parameters of the signature."""
        parameters: dict[ParamName, Param] = {}

        for name, parameter in sig.parameters.items():
            annotation, qualifier = extract_type_info(parameter.annotation)

            if isinstance(annotation, (str, ForwardRef)) and func_module:
                annotation_name = (
                    annotation if isinstance(annotation, str) else annotation.__forward_arg__
                )

                if annotation_name in sys.modules[func_module].__dict__:
                    annotation = sys.modules[func_module].__dict__[annotation_name]

            parameters[name] = Param(
                type=annotation if has_parameter_type(annotation) else AnyType,
                is_positional_only=parameter.kind is Parameter.POSITIONAL_ONLY,
                name=name,
                default=_get_default_value(parameter),
                qualifier=qualifier,
            )

        return parameters


def _get_default_value(parameter: Parameter) -> Any:
    if parameter.default is Parameter.empty:
        return NoDefault
    return parameter.default

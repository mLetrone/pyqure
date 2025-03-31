from functools import wraps
from inspect import Parameter, isclass, signature
from typing import (
    Any,
    Callable,
    ParamSpec,
    Sequence,
    TypeVar,
    overload,
)

from pyqure.container import Alias, DependencyContainer, Key, dc
from pyqure.discover import _get_package_caller, discover
from pyqure.exceptions import InjectionError, MissingDependencies
from pyqure.injectables import (
    Factory,
    Injectable,
    Qualifier,
    Singleton,
)
from pyqure.utils.function import NoDefault, Param, Parameters, ParamName
from pyqure.utils.types import is_interface, unpack_types

T = TypeVar("T")
P = ParamSpec("P")
R = ParamSpec("R")

Service = type[T] | Callable[..., T]


def create_injectable(
    service: Service[T], is_factory: bool = False, *, container: DependencyContainer = dc
) -> Injectable[T]:
    """Create an injectable inline.

    It's an alternative to `@component` or `@factory` decorators, to register a dependency.

    Args:
        service: the service to build an injectable.
        is_factory: option to either create a factory or a singleton.
        container: the container where the service dependencies will be searched.

    Examples:
        >>> container[Key(Service, "my-service")] = create_injectable(Service)
    """
    service_ = _create_new_service_call(service, container)
    if is_factory:
        return Factory(service_)

    return Singleton(service_)


@overload
def component(service: type[T], /) -> type[T]: ...


@overload
def component(service: Callable[P, T], /) -> Callable[P, T]: ...


@overload
def component(
    *,
    container: DependencyContainer = dc,
    qualifier: Qualifier | str | None = None,
    primary: bool = False,
) -> Callable[[Service[T]], Service[T]]: ...


def component(
    service: Service[T] | None = None,
    *,
    container: DependencyContainer = dc,
    qualifier: Qualifier | str | None = None,
    primary: bool = False,
) -> Service[T] | Callable[[Service[T]], Service[T]]:
    """Register a class or a function as a component (`Singleton` injectable).

    * Upon class, all parent classes are automatically registered.
    * Upon **typed** function, all parent classes of the return are automatically registered.

    Args:
        service: function or class to register
        container: the container where registering the service
        qualifier: can be passed to specify an alias to the component,
         and identify it for injection over other components of same type.
        primary: allow to prioritize component over others of same type if no qualifier set for injection.

    Examples:
        >>> @component
        ... class MyService(Service): ...

        >>> @component(qualifier="foo")
        ... class FooService(Service): ...
    """

    def decorator(serv: Callable[P, T] | type[T]) -> Callable[P, T] | type[T]:
        _register(serv, container=container, is_factory=False, qualifier=qualifier, primary=primary)
        return serv

    if service is None:
        return decorator

    return decorator(service)


@overload
def factory(service: type[T], /) -> type[T]: ...


@overload
def factory(service: Callable[..., T], /) -> Callable[..., T]: ...


@overload
def factory(
    *,
    container: DependencyContainer = dc,
    qualifier: Qualifier | str | None = None,
    primary: bool = False,
) -> Callable[[Service[T]], Service[T]]: ...


def factory(
    service: Service[T] | None = None,
    *,
    container: DependencyContainer = dc,
    qualifier: Qualifier | str | None = None,
    primary: bool = False,
) -> Service[T] | Callable[[Service[T]], Service[T]]:
    """Register a class or a function as a factory (`Factory` injectable).

    * Upon class, all parent classes are automatically registered.
    * Upon **typed** function, all parent classes of the return are automatically registered.

    Args:
        service: function or class to register
        container: the container where registering the service
        qualifier: can be passed to specify an alias to the component,
         and identify it for injection over other components of same type.
         For function, qualifier default value is the function name.
        primary: allow to prioritize component over others of same type if no qualifier set for injection.
    """

    def decorator(serv: Service[T]) -> Service[T]:
        _register(serv, container=container, is_factory=True, qualifier=qualifier, primary=primary)
        return serv

    if service is None:
        return decorator

    return decorator(service)


ConfigurationFunc = Callable[[DependencyContainer], Any]


@overload
def configuration(config: None, /) -> Callable[[ConfigurationFunc], ConfigurationFunc]: ...


@overload
def configuration(config: ConfigurationFunc, /) -> ConfigurationFunc: ...


@overload
def configuration(
    *,
    container: DependencyContainer = dc,
    autoload: bool = False,
    packages_to_load: list[str] | None = None,
) -> Callable[[ConfigurationFunc], ConfigurationFunc]: ...


def configuration(
    config: ConfigurationFunc | None = None,
    *,
    container: DependencyContainer = dc,
    autoload: bool = False,
    packages_to_load: list[str] | None = None,
) -> ConfigurationFunc | Callable[[ConfigurationFunc], ConfigurationFunc]:
    """Define a function as container configuration.

    Inside the function, it's possible to register injectables.
    It can be useful to centralize `Constant` injectables at one place.

    Another functionality is to discover from a package, to auto-load the injectables.

    Args:
        autoload: whether to discover injectables or not.
        packages_to_load: from where perform the discovering.
        container: the container where registering the service.
        config: configuration function.

    Examples:
        >>> @configuration
        ... def config(container: DependencyContainer) -> None:
        ...     container[Key(str, "contract_table")] = Constant(os.environ["CONTRACT_TABLE"])
        ...     # Can register as many as you want to!
        ... # Is equivalent to
        >>> @component
        ... def contract_table() -> str:
        ...     return os.environ["CONTRACT_TABLE"]
    """

    def decorator(
        configs: Callable[[DependencyContainer], Any],
    ) -> Callable[[DependencyContainer], Any]:
        if autoload:
            packages: Sequence[str | None] = packages_to_load or [_get_package_caller(2)]  # type: ignore[list-item]
            for pkg in packages:
                discover(pkg)
        configs(container)
        return configs

    if config is None:
        return decorator

    return decorator(config)


@overload
def inject(service: Callable[P, T], /) -> Callable[..., T]: ...


@overload
def inject(
    *,
    container: DependencyContainer = dc,
) -> Callable[[Callable[P, T]], Callable[..., T]]: ...


def inject(
    service: Callable[P, T] | None = None, *, container: DependencyContainer = dc
) -> Callable[..., T] | Callable[[Callable[P, T]], Callable[..., T]]:
    """Marked the function decorated to inject dependencies through parameters.

    Transform it to a dynamic partial function, it can be used passing all the arguments.
    Or passing only some, or even zero, and inject the missing ones with the registered injectables.

    For each parameter the corresponding injectable is searched this way:
        * does a service is registered by this alias key
        * does a service is registered by this type and parameter name key
        * does the parameter is annotated with a qualifier ex: param: Annotated[Service, qualifier("alias")], so look up for a service with Key(Service, "alias")
    """

    def decorator(service_: Callable[P, T]) -> Callable[..., T]:
        return _create_new_service_call(service_, container)

    if service is None:
        return decorator

    return decorator(service)


def _register(
    service: Service[T],
    *,
    container: DependencyContainer,
    qualifier: Qualifier | str | None,
    primary: bool,
    is_factory: bool = False,
) -> Service[T]:
    """**Internal** function to register a service as injectable inside the container."""
    service_ = _create_new_service_call(service, container)
    key = _create_key(service, qualifier)

    if is_factory:
        container.register(key, Factory(service_), primary=primary)
    else:
        container.register(key, Singleton(service_), primary=primary)
    return service_


def _create_key(service: Service[T], qualifier: Qualifier | str | None) -> Key[T]:
    """**Internal** function to create the key of the service."""
    if isclass(service):
        return Key(service, qualifier)

    return_type = signature(service).return_annotation

    if return_type in (Any, Parameter.empty):
        return Alias(qualifier or service.__name__)
    return Key(return_type, qualifier or service.__name__)


def _create_new_service_call(
    service: Service[T], container: DependencyContainer
) -> Service[T] | Callable[..., T]:
    """Create a new service function callable to be either called by its arguments or by injection."""
    if isclass(service) and is_interface(service):
        raise InjectionError(
            f"The service {service} provided is invalid:"
            f" it's impossible to instantiate abstract or protocol classes."
        )
    parameters = Parameters(service)

    @wraps(service)
    def decorator(*args: Any, **kwargs: Any) -> T:
        # If it can be called normally
        if _is_callable_with_binding(service, *args, **kwargs):
            return service(*args, **kwargs)

        # else we search to inject the dependencies
        submitted_args = parameters.partial_bind(args, kwargs)
        all_args = (
            _resolve_arguments_injectable(parameters.missing(kwargs=submitted_args), container)
            | submitted_args
        )

        missing = set(parameters.mandatory) - set(all_args)

        if missing:
            raise MissingDependencies(service, missing)

        return service(**all_args)

    return decorator


def _resolve_arguments_injectable(
    arguments: dict[ParamName, Param], container: DependencyContainer
) -> dict[ParamName, Any]:
    """Resolve for each argument, the available injectable value corresponding to it if it exists.

    Returns:
        A dict of arguments with their value for injection to the service.
    """
    resolved: dict[ParamName, Any] = {}

    for name, arg in arguments.items():
        if Alias(name) in container:
            resolved[name] = container[Alias(name)]
            continue

        for type_ in unpack_types(arg.type):
            if Key(type_, name) in container:
                resolved[name] = container[Key(type_, name)]
                continue
            if Key(type_, arg.qualifier) in container:
                resolved[name] = container[Key(type_, arg.qualifier)]
                continue

        if name not in resolved and arg.default is not NoDefault:
            resolved[name] = arg.default

    return resolved


def _is_callable_with_binding(f: Callable[..., Any], *args: Any, **kwargs: Any) -> bool:
    """Check whether the function is callable with this arguments mapping.

    Returns:
         True if that's the case, otherwise False.
    """
    try:
        signature(f).bind(*args, **kwargs)
    except TypeError:
        return False
    else:
        return True

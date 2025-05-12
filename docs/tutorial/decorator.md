# Decorator

## Concept

Decorators in Python are a very powerful and useful tool
that allows adding behavior/functionality to other functions or classes.

By definition, a decorator is a function taking a callable (function, class) as argument (_the function to be decorated_),
and returning it with or without extra functionalities.

### Callable a first-class citizen

In Python everything is an object, including functions.
This means, function can be passed as argument or store in a variable.

```python
def greet() -> None:
    print("Hello World!")

salutation = greet

salutation()
>>> "Hello World!"
```
### Simple example

With the basics, let's create a simple decorator:

```python
from typing import Callable, Any
from functools import wraps

# Decorated function signature. Here any function.
Func = Callable[..., Any] # (1)!

# Decorator definition
def describe(func: Func) -> Callable[[Func], Any]:
    # preserve function metadata (like documentation)
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Function <{func.__name__}> called with: {args} and {kwargs}.")
        return func(*args, **kwargs)
    return wrapper


def get_full_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name.upper()}"


decorated_get_full_name = describe(get_full_name)

print(decorated_get_full_name("Foo", "Bar"))
>>> Function <get_full_name> called with: ('Foo', 'Bar') and {}.
>>> Foo BAR
```

`Describe` is a decorator that prints the function name and its parameters value when the decorated function is called.
Each time `decorated_get_full_name` is executed, the inner function `wrapper` is called.

#### Explanation
1. `describe` is a function that takes `func` as an argument
2. Inside `describe` the `wrapper` function, is the function adding logic.
3. Return ` wrapper`, this way when `func` is called, it will run `wrapper` instead.


To sum up a decorator is a function (callable) that takes a function,
do something with it, adding logic or register it, and should return a function.

Python allow you to use decorators with the `@` symbol followed by the decorator name,
directly placed above the function definition.

With this syntactic sugar:
```python
@describe
def get_full_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name.upper()}"
```

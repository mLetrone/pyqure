# Python type annotations

!!! note
    If you already know everything about type hints, skip this chapter.

Python is a dynamically typed language, which means declaring types is optional.
That'd simplify _Proof Of Concept_, script or one-shot code creation.
However, this can lead to bugs, ambiguity in your code.

## So what are type hints?

Type hints or annotations are introduced in Python 3.5.
This syntax allows declaring the type of variable, function, etc.
It's a hint for those who read or use code, offering a better understanding of it.

> Like traffic, even though it's possible to drive without signs,
 an accident can happen very quickly.
 It's the same with types: they give you confidence and prevent bugs and errors.


```python
def get_full_name(first_name, last_name):
    return first_name + " " + last_name.title()

# with type hints
def get_full_name(first_name: str, last_name: str) -> str:
    return first_name + " " + last_name.title()
```

The benefits:

- Catch potential bugs before running code.
- Document code
- Improve editor autocompletion.

!!! warning "But, those annotations **are** purely for statics guidance, it doesn't add any type validation at runtime."

Type Hints are not enforced or mandatory by Python, but third-party tools like Pydantic or **Pyqure**,
can use it at runtime.

## Declaring types

### Primitives

You can declare all primitive Python types, not only `str`.

```python
name: str
height: float
age: int
has_licence: bool
file_content: bytes
```

### Collections

Collections are data structures that contain other values;
these types are called "Generics", like ` dict`, ` list`, ` set`, `tuple`, etc.

!!! tip
    Since Python 3.9+, it's no longer necessary to import built-in collection type from `typing`,
    you can subscript them directly.

```python
# List of numbers
exam_marks: list[float] = [12.5, 18, 10]
# Tuple of two numbers
origin: tuple[int, int] = (0, 0)
# Tuple of unlimited strings
months: tuple[str, ...] = ("jan", "feb", "mar", "dec")
# Dictionary
versions: dict[str, list[str]] = {"python": ["3.11", "3.12", "3.13"]}
```

### Functions

In python function are first-class citizens,
so you can declare types not only for function arguments and return, but also the function itself (useful for decorator).

Function signature
```python
def greet(name: str, polite: bool = True) -> str:
    return f"Good morning {name}" if polite else f"Yo {name}!"
```

Variable-length argument and function typing.
```python
from functools import reduce
from collections.abc import Callable

type Operation = Callable[[float, float], float]

def calculate(*numbers: float, operation: Operation) -> float:
    return reduce(operation, numbers)

calculate(1, 2, 3, operation=lambda a,b: a + b)
```

### Union

You can declare that a variable can be any of **several types**, for instance `str` or `int`.

```python
# Means that name can be a str or None
def greet(name: str | None = None) -> str:
    if name is None:
        return "Hello there!"

    return f"Hey {name}!"
```

Your editor can help detect errors where you where assuming that some variable is always a type,
whereas it can be any type of the union.

!!! info
    It was an introduction to type hints, there are still some types to know more about,
    you can check [the cheat sheet from mypy :octicons-link-external-16:](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html){target="_blank"}

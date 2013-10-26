Dispatch
========

A python library for overloading functions on type and signature.

Overview
--------

Sure, `*args` and `**kwargs` are great. But sometimes you need more- you need to
have genuinely distinct behavior based on the types or layout of your arguments.
`dispatch` allows you to do just that. By attaching type annotations to your
functions, and decorating them with dispatch, you can have a group of functions
and automatically determine the correct one to call. No more `elif isinstance`
chains, or `len(args)`, or `arg in kwargs`.

Examples
--------

```python
Basic Usage:

from dispatch import dispatch

@dispatch
def greet(x: int):
    return 'Hello, {} the int!'.format(x)

@greet.dispatch
def greet(x: list):
    return 'Hello everyone!'

@greet.dispatch
def greet(x):
    return 'Hello, mysterious stranger!'

@greet.dispatch
def greet(x: int, y):
    return 'Hello, int and guest!'

@greet.dispatch
def greet(x, y):
    return 'Hello, pair of mysterious strangers!'

assert greet(1) == 'Hello, 1 the int!'
assert greet([1, 2, 3]) == 'Hello everyone!'
assert greet(None) == 'Hello, mysterious stranger!'
assert greet(1, 10) == 'Hello, int and guest!'
assert greet('a', 'b') == 'Hello, pair of mysterious strangers!'
```


Overload on number of arguments to make automatic decorators:

```python
from dispatch import dispatch

#Non-decorator version
@dispatch
def add_return_value(func, additional):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) + additional
    return wrapper

#decorator version.
@add_return_value.dispatch
def add_return_value(additional):
    def decorator(func):
        return add_return_value(func, additional)
    return decorator

plus_one_len = add_return_value(len, 1)
assert plus_one_len([1, 2, 3]) == 4

@add_return_value(10)
def double_add_10(x):
    return x * 2

assert double_add_10(5) == 20
```

Dispatching
===========

A python library for overloading functions on type and signature.

Overview
--------

Sure, `*args` and `**kwargs` are great. But sometimes you need more- you need to
have genuinely distinct behavior based on the types or layout of your arguments.
`dispatching` allows you to do just that. By attaching type annotations to your
functions, and decorating them with `dispatch`, you can have a group of functions
and automatically determine the correct one to call. No more `elif isinstance`
chains, or `len(args)`, or `arg in kwargs`.


Usage
-----

To use dispatching, create a `DispatchGroup` object. This object collects all
the functions that should be tried when executing a dispatch call.

```python
import dispatching
greetings = dispatching.DispatchGroup()
```

To add a function to the dispatch group, decorate it with the `dispatch` member.

```python
@greetings.dispatch
def greet(x: int):
    print("Hello, int!")

@greetings.dispatch
def greet(x: str):
    print("Hello, str!")

greet(1)  # Prints "Hello, int!"
greet('string')  # Prints "Hello, str!"
greet([1, 2, 3])  # Raises DispatchError, a subclass of TypeError
```

The argument annotation determines what function is called. Each function
registered to the group is tried, in order, to have arguments bound to its
parameter signature. The first one that matches is called. If none match, a
DispatchError is raised.

Not every argument needs to have an annotation. Use a completely unannotated
function to create a base case, which will be called if nothing else matches:

```python
@greetings.dispatch
def greet(x):
    print("Hello, mysterious stranger!")

greet([1, 2, 3])  # Prints "Hello, mysterious stranger!"
greet(1)  # Still prints "Hello, int!"
```

Be careful, though. Functions are tried in the order that the are decorated, so
adding additional overloads after a base case won't do any good:

```python
@greetings.dispatch
def greet(x: list):
    print("Hello, list!")

greet([1, 2, 3])  # still prints "Hello, mysterious stranger"
```

To get around this, you can use the dispatch_first decorator, which adds the
function to the front of the list of functions to try:

```python
@greetings.dispatch_first
def greet(x: list):
    print("Hello, list!")

greet([1, 2, 3])  # now prints "Hello, list!"
```

Other usage notes
-----------------

It is not nessesary to explicitly create a DispatchGroup object. Instead, you
can use the global function `dispatch` to create a new `DispatchGroup`
implicitly. The decorated functions will automatically have the `dispatch` and
`dispatch_first` attributes attached to them, so that more overloads can be
added.

```python
@dispatching.dispatch
def half(x: int):
    return x / 2

@half.dispatch
def half(x: str):
    return x[0:len(x)/2]
```

This applies when using an explicit `DispatchGroup` as well. Because everything
has the attributes attached to it, it also isn't necessary to give all functions
the same name, or to give them a different name than the `DispatchGroup`.

In addition to matching by type, you can match by number of arguments:

```python
@dispatching.dispatch
def nargs(a):
    return 1

@nargs.dispatch
def nargs(a, b):
    return 2

@nargs.dispatch
def nargs(a, b, c):
    return 3

assert nargs(1) == 1
assert nargs(5, 4, 3) == 3
assert nargs(2, 4) == 2
#Using less than 1 or more than 3 will raise a DispatchError
```

Or by predicate:

```python
def is_odd(x): return x % 2 == 1
def is_even(x): return x % 2 == 0

@dispatching.dispatch
def evens_only(x: is_even):
    return x

@evens_only.dispatch
def evens_only(x: is_odd)
    raise ValueError(x)
```

Or by value comparison:

```python
#Classic freshman recursion

@dispatching.dispatch
def fib(n: 0):
    return 1

@fib.dispatch
def fib(n: 1)
    return 1

@fib.dispatch
def fib(n):
    return fib(n-1) + fib(n-2)
````

Examples
--------

Overload on number of arguments to make automatic decorators:

```python
from dispatching import dispatch

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

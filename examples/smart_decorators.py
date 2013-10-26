'''
This demonstrates how dispatch can be used to overload on the number of
arguments. For instance, a "smart" decorator can be created, which acts as
a decorator when only one parameter is given, or simply modifies a given
function if two are given.
'''


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

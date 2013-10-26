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

import unittest
import dispatching
from dispatching import DispatchError

class TestDispatching(unittest.TestCase):
    def setUp(self):
        self.dispatch = dispatching.DispatchGroup()

    def test_dispatch_error(self):
        @self.dispatch.dispatch
        def func(x: int):
            return 'int', x

        @self.dispatch.dispatch
        def func(x: str):
            return 'str', x

        self.assertEqual(func(1), ('int', 1))
        self.assertEqual(func('hello'), ('str', 'hello'))
        self.assertRaises(DispatchError, func, 4.5)

    def test_dispatch_noerror(self):
        @self.dispatch.dispatch
        def func(x: int):
            return 'int', x

        @self.dispatch.dispatch
        def func(x):
            return 'other', x

        self.assertEqual(func(1), ('int', 1))
        self.assertEqual(func('hello'), ('other', 'hello'))
        self.assertEqual(func([]), ('other', []))

    def test_partial_dispatch(self):
        @self.dispatch.dispatch
        def func(x: int, y: int):
            return ('int', 'int')

        @self.dispatch.dispatch
        def func(x: int, y):
            return ('int', 'other')

        @self.dispatch.dispatch
        def func(x, y: int):
            return ('other', 'int')

        self.assertEqual(func(1, 2), ('int', 'int'))
        self.assertEqual(func(1, 'hello'), ('int', 'other'))
        self.assertEqual(func('hello', 1), ('other', 'int'))
        self.assertRaises(DispatchError, func, 'hello', 'world')

    def test_bad_dispatch_order(self):
        @self.dispatch.dispatch
        def func(x: str):
            return 'str'

        @self.dispatch.dispatch
        def func(x):
            return 'other'

        @self.dispatch.dispatch
        def func(x: int):
            return 'int'

        self.assertEqual(func('hello'), 'str')
        self.assertEqual(func([]), 'other')
        self.assertEqual(func(1), 'other')

    def test_custom_type(self):
        class Foo:
            pass

        class Bar:
            pass

        @self.dispatch.dispatch
        def func(x: Foo):
            return 'Foo'

        @self.dispatch.dispatch
        def func(x: Bar):
            return 'Bar'

        self.assertEqual(func(Foo()), 'Foo')
        self.assertEqual(func(Bar()), 'Bar')
        self.assertRaises(DispatchError, func, 1)

    def test_inheritance(self):
        class Foo:
            pass

        class Bar(Foo):
            pass

        @self.dispatch.dispatch
        def func(x: Foo):
            return 'Foo'

        self.assertEqual(func(Foo()), 'Foo')
        self.assertEqual(func(Bar()), 'Foo')
        self.assertRaises(DispatchError, func, 1)

    def test_inversion_pattern(self):
        @self.dispatch.dispatch
        def func(x: int, y):
            return 'int'

        @self.dispatch.dispatch
        def func(x, y: int):
            return func(y, x)

        @self.dispatch.dispatch
        def func(x, y):
            return 'other'

        self.assertEqual(func(1, 1), 'int')
        self.assertEqual(func(1, 'a'), 'int')
        self.assertEqual(func('a', 1), 'int')
        self.assertEqual(func('a', 'a'), 'other')

    def test_raises(self):
        '''
        Ensure that TypeErrors raised by the dispatched function aren't
        caught
        '''
        @self.dispatch.dispatch
        def func(x: int):
            return 'int'

        @self.dispatch.dispatch
        def func(x: str):
            return 'str'

        @self.dispatch.dispatch
        def func(x: list):
            raise TypeError('non dispatch')

        self.assertEqual(func(1), 'int')
        self.assertEqual(func('a'), 'str')
        self.assertRaisesRegex(TypeError, 'non dispatch', func, [])
        self.assertRaises(DispatchError, func, 1.5)

    def test_attribute(self):
        @dispatching.dispatch
        def func(x: int):
            return 'int'

        @func.dispatch
        def func(x: str):
            return 'str'

        self.assertEqual(func(1), 'int')
        self.assertEqual(func('a'), 'str')
        self.assertRaises(DispatchError, func, [])

    def test_dispatch_first(self):
        class Foo:
            pass

        class Bar(Foo):
            pass

        @self.dispatch.dispatch
        def func(x: Foo):
            return 'Foo'

        @self.dispatch.dispatch
        def func(x):
            return 'other'

        self.assertEqual(func(Foo()), 'Foo')
        self.assertEqual(func(Bar()), 'Foo')
        self.assertEqual(func(1), 'other')

        @self.dispatch.dispatch_first
        def func(x: Bar):
            return 'Bar'

        self.assertEqual(func(Bar()), 'Bar')
        self.assertEqual(func(Foo()), 'Foo')

    def test_value_match(self):
        #Classic freshman recursions
        @self.dispatch.dispatch
        def length_of_list(x: []):
            return 0

        @self.dispatch.dispatch
        def length_of_list(x: list):
            return length_of_list(x[1:]) + 1

        self.assertEqual(length_of_list([1, 2, 3]), 3)
        self.assertEqual(length_of_list([]), 0)
        self.assertRaises(DispatchError, length_of_list, ())

    def test_predicate_match(self):
        is_even = lambda x: x % 2 == 0
        is_odd = lambda x: x % 2 == 1

        #print for even, raise for odd
        @self.dispatch.dispatch
        def evens_only(x: is_even):
            return x / 2

        @self.dispatch.dispatch
        def evens_only(x: is_odd):
            raise ValueError

        self.assertEqual(evens_only(0), 0)
        self.assertEqual(evens_only(10), 5)
        self.assertRaises(ValueError, evens_only, 5)

    def test_self_kwarg(self):
        @self.dispatch.dispatch
        def func(x, y, self: int):
            return x, y, self + 10

        @self.dispatch.dispatch
        def func(x, y, self: str):
            return x, y, self

        self.assertEqual(
            self.dispatch(y=1, self=2, x=3),
            (3, 1, 12))
        self.assertEqual(
            self.dispatch(self='a', x='b', y='c'),
            ('b', 'c', 'a'))

    def test_varargs_all(self):
        '''
        Check that annotations on *args effect the whole tuple of args
        '''
        def is_length(n):
            return lambda x: len(x) == n

        @self.dispatch.dispatch
        def func(*args: is_length(1)):
            return 1

        @self.dispatch.dispatch
        def func(*args: is_length(2)):
            return 2

        self.assertEqual(func(1), 1)
        self.assertEqual(func(1, 2), 2)
        self.assertRaises(DispatchError, func, 1, 2, 3)

    def test_varargs_each(self):
        '''
        Test the all_match function
        '''
        @self.dispatch.dispatch
        def combine(*args: dispatching.all_match(int)):
            return sum(args)

        @self.dispatch.dispatch
        def combine(*args: dispatching.all_match(str)):
            return ''.join(args)

        self.assertEqual(combine(1, 2, 3), 6)
        self.assertEqual(combine('Hello ', 'World'), "Hello World")
        self.assertRaises(DispatchError, combine, 1, "x")

class TestDispatchIntrospection(unittest.TestCase):
    def setUp(self):
        self.dispatch = dispatching.DispatchGroup()
        def func1(x: int):
            pass

        def func2(x: list):
            pass

        def func3(x: str):
            pass

        self.dispatch.dispatch(func1)
        self.dispatch.dispatch(func2)
        self.dispatch.dispatch(func3)

        self.funcs = [func1, func2, func3]

    def test_registered_functions(self):
        #Use a set. No guarentee about order.
        self.assertEqual(set(self.dispatch.registered_functions),
            set(self.funcs))

    def test_lookup_explicit(self):
        self.assertIs(
            self.dispatch.lookup_explicit([1], {}),
            self.funcs[0])
        self.assertIs(
            self.dispatch.lookup_explicit([[1, 2, 3]], {}),
            self.funcs[1])
        self.assertIs(
            self.dispatch.lookup_explicit(['hello'], {}),
            self.funcs[2])
        self.assertIs(
            self.dispatch.lookup_explicit([], {'x': 1}),
            self.funcs[0])

        self.assertRaises(DispatchError,
            self.dispatch.lookup_explicit, [1.5], {})

    def test_lookup(self):
        self.assertIs(
            self.dispatch.lookup(1),
            self.funcs[0])
        self.assertIs(
            self.dispatch.lookup([1, 2, 3]),
            self.funcs[1])
        self.assertIs(
            self.dispatch.lookup('hello'),
            self.funcs[2])
        self.assertIs(
            self.dispatch.lookup(x=1),
            self.funcs[0])

        self.assertRaises(DispatchError,
            self.dispatch.lookup, 1.5)

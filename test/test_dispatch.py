import unittest
import dispatch
from dispatch import DispatchError

class TestDispatch(unittest.TestCase):
    def setUp(self):
        self.dispatch = dispatch.DispatchGroup()

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
        @dispatch.dispatch
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

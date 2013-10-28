'''
Dispatch provides methods to define multiple call signatures for the
same function.
'''

from inspect import signature, Parameter
from functools import wraps, partial
from collections import deque

class DispatchError(TypeError):
    pass

class DispatchGroup():
    '''
    A DispatchGroup object manages the type dispatch for a group of functions.
    when a function in the DispatchGroup is called, it attempts to bind the
    arguments to the type signature of each grouped function in the order they
    were added to the group. It calls the first matching function, and raises
    a DispatchError (a subclass of TypeError) if no function matched.
    '''
    __slots__ = ['callees']

    def __init__(self):
        '''
        callees is a list of (bind_args, function) pairs. bind_args is a
        function that, when called with the arguments, attempts to bind them
        in a way that matches function's type signature, or raises a TypeError
        on failure.'''
        self.callees = deque()

    @staticmethod
    def bind_args(sig, param_matchers, args, kwargs):
        '''
        Attempt to bind the args to the type signature. First try to just bind
        to the signature, then ensure that all arguments match the parameter
        types.
        '''
        #Bind to signature. May throw its own TypeError
        bound = sig.bind(*args, **kwargs)

        if not all(param_matcher(bound.arguments[param_name])
                for param_name, param_matcher in param_matchers):
            raise TypeError

        return bound

    @staticmethod
    def _make_param_matcher(annotation):
        '''
        For a given annotation, return a function which, when called on a
        function argument, returns true if that argument matches the annotation.
        If the annotation is a type, it calls isinstance; if it's a callable,
        it calls it on the object; otherwise, it performs a value comparison.
        '''
        if isinstance(annotation, type):
            return (lambda x: isinstance(x, annotation))
        elif callable(annotation):
            return (lambda x: annotation(x))
        else:
            return (lambda x: x == annotation)

    @classmethod
    def _make_all_matchers(cls, parameters):
        '''
        For every parameter, create a matcher if the parameter has an
        annotation.
        '''
        for name, param in parameters:
            if param.annotation is not Parameter.empty:
                yield name, cls._make_param_matcher(param.annotation)

    @classmethod
    def _make_dispatch(cls, func):
        '''
        Create a dispatch pair for func- a tuple of (bind_args, func), where
        bind_args is a function that, when called with (args, kwargs), attempts
        to bind those args to the type signature of func, or else return a
        TypeError
        '''
        sig = signature(func)
        param_matchers = list(cls._make_all_matchers(sig.parameters.items()))
        return (partial(cls.bind_args, sig, param_matchers), func)

    def dispatch(self, func):
        '''
        Adds the decorated function to this dispatch.
        '''
        self.callees.append(self._make_dispatch(func))
        return self

    def dispatch_first(self, func):
        '''
        Adds the decorated function to this dispatch, at the FRONT of the order.
        Useful for allowing third parties to add overloaded functionality
        to be executed before default functionality.
        '''
        self.callees.appendleft(self._make_dispatch(func))
        return self

    def execute_dispatch(self, args, kwargs):
        '''
        Dispatch a call. Call the first function whose type signature matches
        the arguemts.
        '''
        for bind_args, callee in self.callees:
            try:
                #bind to the signature and types. Raises TypeError on failure
                bound = bind_args(args, kwargs)
            except TypeError:
                #TypeError: failed to bind arguments. Try the next dispatch
                continue

            #All the parameters matched. Call the function.
            return callee(*bound.args, **bound.kwargs)

        #Nothing was able to bind. Error.
        raise DispatchError(args, kwargs, self)

    def __call__(*args, **kwargs):
        return args[0].execute_dispatch(args[1:], kwargs)

def dispatch(func):
    '''
    Create a new dispatch on func. Bind additional dispatches with
    @func.dispatch
    '''
    return DispatchGroup().dispatch(func)

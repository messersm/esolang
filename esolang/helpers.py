"""A collection of helpers for writing esolang interpreters."""

import inspect
import sys

from warnings import warn

from collections import deque

if sys.version_info.major < 3:
    getfullargspec = inspect.getargspec
else:
    getfullargspec = inspect.getfullargspec


def count_args(f):
    """Return the number of non-optional arguments f takes.

    Args:
        f (callable): any callable (function, method, classmethod, ...)

    Returns:
        int: The number of arguments f takes

    Raises:
        TypeError: If the given function is not supported by
                   inspect.getfullargspec (e.g. some builtins).
    """

    count = len(getfullargspec(f).args)
    if inspect.ismethod(f):
        return count - 1
    else:
        return count


def flow(*args):
    """Returns a function, that executes the

    Examples:
        >>> f1 = lambda a: a**2
        >>> f2 = lambda: 2
        >>> f3 = lambda a, b: a + b
        >>> f = flow(f3, f2, f1, 5)
        >>> f()
        27

    Example for working with classes:
        >>> class A(object):
        ...     def square(self, value):
        ...         return value**2
        >>> a = A()
        >>> f = flow(a.square, 20)
        >>> f()
        400

    Example for working with functions, that return functions:
        >>> from operator import add, sub, mul, floordiv
        >>> from random import choice
        >>> def be_crazy():
        ...     return choice([add, sub, mul, floordiv])
        >>> f = flow(be_crazy, 30, 5)
        >>> result = f()
        >>> result in [35, 25, 150, 6]
        True
    """
    def f():
        # Important: We need to make a copy of args, because
        # f could be called multiple times.
        left = list(args)
        right = deque()

        while left:
            item = left.pop()
            if callable(item):
                func = item

                # Build a list of arguments for the callable taking from right.
                func_args = []
                try:
                    for _ in range(count_args(func)):
                        func_args.append(right.popleft())
                    result = func(*func_args)
                except TypeError:
                    # call func, with incrementally more arguments
                    # until a call succeeds.
                    while True:
                        try:
                            result = func(*func_args)
                            break
                        except TypeError:
                            if not right:
                                raise
                            func_args.append(right.popleft())

                left.append(result)
            else:
                right.appendleft(item)
        if len(right) == 0:
            return
        elif len(right) == 1:
            return right.popleft()
        else:
            t = tuple(right)
            warn("flow() has remaining values on right queue: %s" % str(t))
            return t

    return f


def stackop(func, stack):
    """Returns a function, that operates on the elements of a given stack.

    Example for creating a multiply stack operation,
    which takes two arguments:
        >>> stack = [1, 2, 3, 4]
        >>> multiply = stackop(lambda x, y: x * y, stack)
        >>> multiply()
        >>> stack
        [1, 2, 12]

    Example for creating a square operation,
    which takes one argument:
        >>> stack = [1, 2, 3, 4]
        >>> square = stackop(lambda x: x**2, stack)
        >>> square()
        >>> stack
        [1, 2, 3, 16]

    Example for creating a pop operation,
    which removes the last element from the stack:
        >>> stack = [1, 2, 3, 4]
        >>> pop = stackop(lambda x: None, stack)
        >>> pop()
        >>> stack
        [1, 2, 3]

    Example for a duplicate operation,
    which duplicates the last element of the stack:
        >>> stack = [1, 2, 3, 4]
        >>> duplicate = stackop(lambda x: [x, x], stack)
        >>> duplicate()
        >>> stack
        [1, 2, 3, 4, 4]
    """

    if not callable(func):
        raise TypeError("%s is not callable." % func)

    def f():
        args = []

        argcount = count_args(func)
        for _ in range(argcount):
            args.append(stack.pop())

        results = func(*args)
        if results is None:
            pass
        else:
            # if results is an iterable, put
            # all return values on the stack
            try:
                for r in results:
                    stack.append(r)
            except TypeError:
                stack.append(results)

    return f


class Register(object):
    def __init__(self, value=0):
        self.value = value

    def put(self, value):
        self.value = value

    def get(self):
        return self.value

    def peek(self):
        return self.value


class Fifo(deque):
    """Provides a Fifo (first in first out) datatype.

    Example:
        >>> f = Fifo()
        >>> f.put(20)
        >>> f.put(10)
        >>> f.get()
        20
        >>> f.get()
        10
    """

    def __init__(self, pop_default=None, peek_default=None):
        super(Fifo, self).__init__()

        self.pop_default = pop_default
        self.peek_default = peek_default

    def put(self, value):
        self.append(value)

    def peek(self):
        if len(self) > 0:
            return self[0]
        elif self.peek_default is None:
            raise IndexError("Fifo has no elements.")
        else:
            return self.peek_default()

    def get(self):
        if len(self) > 0:
            return self.popleft()
        elif self.pop_default is None:
            raise IndexError("Fifo has no elements.")
        else:
            return self.pop_default()


class FileBuffer(object):
    def __init__(self, fd):
        self.fd = fd
        self.buffer = deque()

    def get(self):
        if not self.buffer:
            return self.fd.read(1)
        else:
            return self.buffer.popleft()

    def put(self, char):
        self.buffer.appendleft(char)

"""A collection of helpers for writing esolang interpreters."""

import inspect
import sys

if sys.version_info.major < 3:
    def count_args(f):
        return len(inspect.getargspec(f).args)
else:
    def count_args(f):
        return len(inspect.getfullargspec(f).args)


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

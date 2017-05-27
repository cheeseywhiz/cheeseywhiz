#!/usr/bin/env python3


def vector_1d(f):
    """Take first argument in decorated function and evaluate across all
    elements in the argument.
    Returns a list equal in size to the given list."""
    def decorator(list, *args, **kwargs):
        return [f(item, *args, **kwargs) for item in list]

    return decorator

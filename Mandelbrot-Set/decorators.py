#!/usr/bin/env python3

from time import clock
from numpy import vectorize


def timer(f):
    """Decorated function prints execution time to console."""
    def decorator(*args, **kwargs):
        t = clock()
        res = f(*args, **kwargs)
        print('%.6f'%(clock() - t))
        return res
    return decorator


def np_vector(f):
    """Decorated function is a numpy vectorized function."""
    def decorator(*args, **kwargs):
        return (vectorize(f))(*args, **kwargs)
    return decorator

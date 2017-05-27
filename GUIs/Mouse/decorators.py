#!/usr/bin/env/python3

from time import clock


def foreach(f):
    def decorator(*args, **kwargs):
        for i, j in zip(args[0], args[1]):
            new_args = [i, j]
            for arg in args[2:]:
                new_args.append(arg)
            f(*new_args, **kwargs)
    return decorator


def timer(f):
    """Decorated function prints execution time to console"""
    def decorator(*args, **kwargs):
        t = clock()
        res = f(*args, **kwargs)
        print('%.6f'%(clock() - t))
        return res
    return decorator

import collections
import functools
import pickle
import subprocess


DownloadResult = collections.namedtuple('DownloadResult', (
    'succeeded', 'status', 'url', 'fname', 'content'))


class DownloadCache:
    """A pickle I/O tool"""

    def __init__(self, path):
        self.path = path

    def read(self):
        """Read and parse the pickle at the specified path"""
        with open(self.path, 'rb') as file:
            return pickle.load(file)

    def write(self, object):
        """Write the pickle of {object} at path"""
        with open(self.path, 'wb') as file:
            return pickle.dump(object, file)

    def clear(self):
        """Delete the cache"""
        subprocess.Popen(
            ['rm', self.path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).wait()

    def __repr__(self):
        return (
            f'{self.__class__.__module__}.{self.__class__.__name__}'
            f'({self.path !r})'
        )


class _Cache:
    """Wrapper class to implement cache decorator"""

    def __init__(self, func, cache):
        self.__func = func
        self.cache = cache

    def __call__(self, *args, **kwargs):
        key = functools._make_key(args, kwargs, False)

        try:
            result = self.cache[key]
        except KeyError:
            new = self.__func(*args, **kwargs)
            self.cache[key] = new
            return new
        else:
            return result

    def __repr__(self):
        cache = repr(self.cache)

        if len(cache) > 384:
            cache = cache[:384] + '...' + cache[-1]

        return (
            f'{self.__class__.__module__}.{self.__class__.__name__}'
            f'({self.__func !r}, {cache})'
        )


def cache(load=None):
    """Small reimplementation of functools.lru_cache(maxsize=None, typed=False)
    that has an accessible cache"""
    if load is None:
        load = {}

    def decorator(func):
        new_func = _Cache(func, load)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return new_func(*args, **kwargs)

        return wrapper

    return decorator

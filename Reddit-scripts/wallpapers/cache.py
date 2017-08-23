import collections
import functools
import pickle
import subprocess


DownloadResult = collections.namedtuple('DownloadResult', (
    'succeeded', 'status', 'url', 'fname', 'content'))


class DownloadCache:
    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path, 'rb') as file:
            return pickle.load(file)

    def write(self, object):
        with open(self.path, 'wb') as file:
            return pickle.dump(object, file)

    def clear(self):
        subprocess.Popen(
            ['rm', self.path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).wait()
        subprocess.Popen(
            ['touch', self.path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).wait()


class Cache:
    def __init__(self, func, cache):
        self.__func = func
        self.cache = cache

    def __call__(self, *args, **kwargs):
        """Cache wrapper around specified function."""
        key = functools._make_key(args, kwargs, False)

        try:
            result = self.cache[key]
        except KeyError:
            new = self.__func(*args, **kwargs)
            self.cache[key] = new
            return new
        else:
            return result


def cache(load=None):
    if load is None:
        load = {}

    def decorator(func):
        wrapper = Cache(func, load)
        wrapper = functools.update_wrapper(wrapper, func)
        return wrapper

    return decorator


@cache()
def fib(n):
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)

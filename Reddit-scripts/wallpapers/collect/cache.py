"""Provides objects for caching"""
import collections
import contextlib
import functools
import pickle

from . import util

_new_named_tuple_repr = """\
    def __repr__(self):
        module = self.__class__.__module__
        return f'<{{module}}.{typename} object at {{hex(id(self))}}>'
"""
collections._class_template = collections._class_template.replace(
    '    def __repr__(self):', _new_named_tuple_repr)
DownloadResult = collections.namedtuple('DownloadResult', (
    'url', 'time', 'succeeded', 'status', 'fname', 'content'))


class CacheBase:
    """Contains helper functions for Cache object __repr__ methods."""
    __slots__ = ()

    def filter_func(self, name, value):
        """Method that decides how to filter kwargs for representation."""
        new_name = ''.join(('_', name, '_arg'))
        old_name = getattr(self, name)
        return getattr(self, new_name, old_name)

    @classmethod
    def make_repr(cls, *args, **kwargs):
        """Format a repr from args and kwargs."""
        name = '.'.join((cls.__module__, cls.__name__))
        parts = list(map(repr, args))
        parts.extend(f'{name}={value !r}' for name, value in kwargs.items())

        return f"{name}({', '.join(parts)})"


class PickleIO(CacheBase):
    """Given a path, read or write the pickle of an object at that path."""

    def __init__(self, *args, path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path

    def read(self):
        """Parse the pickle at the given path."""
        try:
            file = open(self.path, 'rb')
        except FileNotFoundError:
            return {}

        with file:
            try:
                return pickle.load(file)
            except EOFError:
                return {}

    def write(self, object):
        """Write the pickle an object at the given path."""
        with open(self.path, 'wb') as file:
            return pickle.dump(object, file, pickle.HIGHEST_PROTOCOL)

    def reinit(self):
        """Reinitialize the cache file."""
        for cmd in 'rm', 'touch':
            util.disown(cmd, self.path)

    def __repr__(self):
        return super().make_repr(path=self.path)


class CacheFunc(CacheBase):
    """functools.lru_cache(max_size=None, typed=False) implementation with an
    accessible cache attribute."""

    def __init__(self, *args, func=None, cache=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.func = func
        self.cache = {}

        if cache is not None:
            self.cache.update(cache)

    def __call__(self, *args, **kwargs):
        key = functools._make_key(args, kwargs, False)

        try:
            result = self.cache[key]
        except KeyError:
            result = self.cache[key] = self.func(*args, **kwargs)
        finally:
            return result

    def __repr__(self):
        kwargs = util.filter_dict(super().filter_func, cache=self.cache)
        return super().make_repr(self.func, **kwargs)


class Cache(PickleIO, CacheFunc):
    """Class with PickleIO and CacheFunc mixed in."""

    def __init__(self, func=None, *, path=None, cache=None):
        super().__init__(func=func)
        self.re_init_self(path=path, cache=cache)

    def re_init_self(self, *, path=None, cache=None):
        super().__init__(func=self.func, path=path)
        self._path_arg = path is not None
        self._cache_arg = cache is not None

        if self._cache_arg:
            self.cache.update(cache)
        elif self._path_arg:
            self.cache.update(self.read())

        return self

    @contextlib.contextmanager
    def saving(self):
        """Context manager: save the cache at the end of the scope."""
        try:
            yield self
        finally:
            self.save_cache()

    def save_cache(self):
        """Save the cache to the specified file"""
        return super().write(self.cache)

    def re_init_cache(self):
        """Reinit the file and currently loaded cache."""
        super().reinit()
        self.cache = {}

    def __repr__(self):
        kwargs = util.filter_dict(
            super().filter_func,
            path=self.path, cache=self.cache)
        return super().make_repr(self.func, **kwargs)


def cache(*, path=None, load=None):
    """Small reimplementation of functools.lru_cache(maxsize=None, typed=False)
    that has an accessible cache"""
    def decorator(wrapped):
        return Cache(wrapped, path=path, cache=load)

    return decorator

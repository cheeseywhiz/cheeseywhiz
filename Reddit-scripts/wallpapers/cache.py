import collections
import functools
import pickle
import util

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
    def __init__(self, func=None, *, path=None, cache=None):
        self._path_arg = bool(path)
        self._cache_arg = bool(cache)
        self.func = func
        self.path = path

        if self._path_arg:
            self.cache = self.read()
        elif self._cache_arg:
            self.cache = cache
        else:
            self.cache = {}

    def _filter_func(self, name, value):
        new_name = ''.join(('_', name, '_arg'))
        old_name = getattr(self, name)
        return getattr(self, new_name, old_name)

    @classmethod
    def _make_repr(cls, args=None, kwargs=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        name = '.'.join((cls.__module__, cls.__name__))

        parts = list(map(repr, args))
        parts.extend(f'{name}={value !r}' for name, value in kwargs.items())

        return f"{name}({', '.join(parts)})"

    def __repr__(self):
        kwargs = util.filter_kwargs(
            self._filter_func,
            func=self.func, path=self.path,
            cache=self.cache)
        return self._make_repr(kwargs=kwargs)


class PickleIO(CacheBase):
    def read(self):
        """Read and parse the pickle at the specified path"""
        with open(self.path, 'rb') as file:
            try:
                return pickle.load(file)
            except (EOFError, FileNotFoundError):
                return {}

    def write(self, object):
        """Write the pickle of {object} at path"""
        with open(self.path, 'wb') as file:
            return pickle.dump(object, file, pickle.HIGHEST_PROTOCOL)

    def init(self):
        """Reinitialize the cache file"""
        for cmd in 'rm', 'touch':
            util.disown(cmd, self.path)

    def __repr__(self):
        kwargs = util.filter_kwargs(None, path=self.path)
        return self._make_repr(kwargs=kwargs)


class CacheFunc(CacheBase):
    def __call__(self, *args, **kwargs):
        key = functools._make_key(args, kwargs, False)

        try:
            result = self.cache[key]
        except KeyError:
            result = self.cache[key] = self.func(*args, **kwargs)
        finally:
            return result

    def __repr__(self):
        args = self.func,
        kwargs = util.filter_kwargs(None, cache=self.cache)
        return self._make_repr(args, kwargs)


class Cache(PickleIO, CacheFunc):
    def save_cache(self):
        """Save the cache to the specified file"""
        return self.write(self.cache)

    def __repr__(self):
        args = self.func,
        kwargs = util.filter_kwargs(
            self._filter_func,
            path=self.path, cache=self.cache)
        return self._make_repr(args, kwargs)


def cache(*, path=None, load=None):
    """Small reimplementation of functools.lru_cache(maxsize=None, typed=False)
    that has an accessible cache"""
    def decorator(wrapped):
        return Cache(wrapped, path=path, cache=load)

    return decorator

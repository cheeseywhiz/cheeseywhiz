import collections
import functools
import os
import pickle
import subprocess


def trim_repr(object):
    class TrimRepr(type(object)):
        def __init__(self, object):
            self.object = object

        def __repr__(self):
            name = self.object.__class__.__name__
            module = self.object.__class__.__module__
            id_ = id(self.object)

            return f'<{module}.{name} object at {hex(id_)}>'

    return TrimRepr(object)


# copy/paste from pywal.util with slight modification
def disown(*cmd):
    """Call a system command in the background, disown it and hide it's
    output."""
    return subprocess.Popen(
        ["nohup", *cmd],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp)


DownloadResult = collections.namedtuple('DownloadResult', (
    'url', 'time', 'succeeded', 'status', 'fname', 'content'))


def _make_repr(name, *, args=(), kwargs={}, module=None):
    if kwargs is None:
        kwargs = {}

    parts = [repr(arg) for arg in args]
    parts.extend(f'{name}={value !r}' for name, value in kwargs.items())

    if module:
        name = '.'.join((module, name))

    return f"{name}({', '.join(parts)})"


class _DownloadCache:
    """A pickle I/O tool"""

    def __init__(self, path=None):
        self.path = path

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
            return pickle.dump(object, file)

    def clear(self):
        """Delete the cache"""
        for cmd in 'rm', 'touch':
            disown(cmd, self.path)

    def __repr__(self):
        name = self.__class__.__name__
        module = self.__class__.__module__
        args = self.path,
        return _make_repr(name, args=args, module=module)


class _Cache(_DownloadCache):
    """Cache decorator implementation.
    init with either path to pickle cache or dict of cache, or neither.
    Set path attribute to read/write later."""

    def __init__(self, func=None, *, path=None, cache=None):
        super().__init__(path=path)
        self.path_arg = bool(path)
        self.cache_arg = bool(cache)
        self.__func = func

        if self.path_arg:
            self.cache = self.read()
        elif self.cache_arg:
            self.cache = cache
        else:
            self.cache = {}

    def save_cache(self):
        """Save the cache to the specified path"""
        return self.write(self.cache)

    def __call__(self, *args, **kwargs):
        key = functools._make_key(args, kwargs, False)

        try:
            result = self.cache[key]
        except KeyError:
            result = self.cache[key] = self.__func(*args, **kwargs)
        finally:
            return result

    def __repr__(self):
        name = self.__class__.__name__
        module = self.__class__.__module__
        args = self.__func,
        kwargs = filter(None, [
            ('path', self.path) if self.path_arg else None,
            ('cache', trim_repr(self.cache)) if self.cache_arg else None,
        ])
        kwargs = dict(kwargs)

        return _make_repr(name, args=args, kwargs=kwargs, module=module)


def cache(*, path=None, load=None):
    """Small reimplementation of functools.lru_cache(maxsize=None, typed=False)
    that has an accessible cache"""
    def decorator(wrapped):
        wrapper = _Cache(wrapped, path=path, cache=load)

        return functools.update_wrapper(wrapper, wrapped)

    return decorator

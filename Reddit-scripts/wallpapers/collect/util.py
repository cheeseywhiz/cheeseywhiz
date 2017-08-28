"""Provides general utility functions"""
import functools
import inspect
import os
import subprocess

VERBOSE = True


# copy/paste from pywal.util with slight modification
def disown(*cmd):
    """Call a system command in the background, disown it and hide it's
    output."""
    return subprocess.Popen(
        ["nohup", *cmd],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp)


def ping(ip_address='8.8.8.8'):
    """Internet connection test"""
    return not disown('ping', '-c 1', '-w 1', ip_address).wait()


def filter_dict(__func, *args, **kwargs):
    """Filter adaptation for dicts. __func is the filter function a la filter()
    and args and kwargs are passed to dict(). if __func is None than it filters
    based on the bool value of the value of each item."""
    if __func is None:
        __func = (lambda name, value: bool(value))

    return {
        name: value
        for name, value in dict(*args, **kwargs).items()
        if __func(name, value)}


_no_doc_module = list(functools.WRAPPER_ASSIGNMENTS)
_removed = ['__doc__', '__module__']

for name in _removed:
    _no_doc_module.remove(name)


@functools.wraps(functools.partial, assigned=_no_doc_module)
def partial(func, *args, **kwargs):
    """partial(func, *args, **kwargs)
    functools.partial as a decorator for top level functions.
    Able to wrap itself with 0-2 yield statements where the second yields a
    function that takes the result as an argument."""
    partial_func = functools.partial(func, *args, **kwargs)
    func_sig = inspect.signature(partial_func)

    def decorator(wrapped):
        @functools.wraps(wrapped, assigned=('__module__', '__qualname__'))
        @functools.wraps(func)
        def wrapper(*wargs, **wkwargs):
            func_generator = wrapped(*wargs, **wkwargs)

            if func_generator is not None:
                next(func_generator)

            result = partial_func(*wargs, **wkwargs)

            try:
                next(func_generator)(result)
            finally:
                return result

        wrapper.__signature__ = func_sig

        if wrapped.__doc__:
            wrapper.__doc__ = wrapped.__doc__

        return wrapper

    return decorator


class _NoneRepr:
    def __repr__(self):
        return repr(None)


_none_repr = _NoneRepr()


def rich_message(*values, beginning=None, label=None, sep=None,
                 **print_kwargs):
    """{beginning}{label}{value}{sep}{value}{sep}{value}{end} > file"""
    if not VERBOSE:
        return

    if not __debug__:
        kwargs = {'beginning': beginning, 'label': label, 'sep': sep,
                  **print_kwargs}
        print('Called with', values, kwargs)

    if sep is None:
        sep = ' '

    print_func = functools.partial(
        functools.partial(print, flush=True),
        **print_kwargs)

    parts = [beginning, label]

    for i, value in enumerate(values, 1):
        if value is None:
            # mimick print(None) which prints 'None'
            value = _none_repr
        parts.append(value)
        if i != len(values):
            parts.append(sep)

    final = ''.join(str(part) for part in parts if part is not None)
    print_func(final)

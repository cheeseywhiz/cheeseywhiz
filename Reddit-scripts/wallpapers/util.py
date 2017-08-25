import functools
import inspect

_no_doc_module = list(functools.WRAPPER_ASSIGNMENTS)
_removed = ['__doc__', '__module__']

for name in _removed:
    _no_doc_module.remove(name)


@functools.wraps(functools.partial, assigned=_no_doc_module)
def partial(func, *args, **kwargs):
    """partial(func, *args, **kwargs)
    functools.partial as a decorator for top level functions.
    Able to wrap itself with 0-2 yield statements where the second yields a
    function that takes the result as an argument"""
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


class NoneRepr:
    def __repr__(self):
        return repr(None)


def _rich_message(*values, beginning=None, label=None, sep=None,
                  **print_kwargs):
    """{beginning}{label}{value}{sep}{value}{sep}{value}{end} > file"""
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
            value = NoneRepr()
        parts.append(value)
        if i != len(values):
            parts.append(sep)

    final = ''.join(str(part) for part in parts if part is not None)
    print_func(final)

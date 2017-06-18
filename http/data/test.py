def gen_vector(dim=0):
    def with_args(f):
        def decorator(obj, *args, _d=dim, **kwargs):
            try:
                iter(obj)
                if _d == 1:
                    raise TypeError
            except TypeError:
                return f(obj, *args, **kwargs)
            else:
                return (
                    decorator(item, *args, _d=_d - 1, **kwargs)
                    for item in obj)
        return decorator
    return with_args


@gen_vector(2)
def f(coords):
    enum = enumerate(coords)
    evens = (val for i, val in enum if not i % 2)
    odds = (val for i, val in enum if i % 2)
    return zip(evens, odds)


def expand(obj, dim=-1):
    try:
        iter(obj)
        if dim == 1:
            raise TypeError
    except TypeError:
        return obj
    else:
        return [expand(item, dim=dim - 1) for item in obj]


def generator(obj, dim=-1):
    try:
        iter(obj)
        if dim == 1:
            raise TypeError
    except TypeError:
        return obj
    else:
        return (generator(item, dim=dim - 1) for item in obj)


coords = [[0, 0, 3, 4, 5, 0], [4, 3, 2, 7]]
coords = generator(coords)

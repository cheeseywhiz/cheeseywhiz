import csv
import sys
from time import clock
import matplotlib.pyplot as plt
from config import data_sets


def timer(f):
    """
    Print execution time of decorated function.
    """
    def decorator(*args, **kwargs):
        t = clock()
        res = f(*args, **kwargs)
        print(f'{(clock() - t):.6f}')
        return res
    return decorator


def vector(dim=-1):
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


def expand(obj, dim=-1):
    try:
        iter(obj)
        if dim == 1:
            raise TypeError
    except TypeError:
        return obj
    else:
        return [expand(item, dim=dim - 1) for item in obj]


try:
    sys.argv[1]
    if sys.argv[1] not in data_sets:
        raise IndexError
except IndexError as error:
    keys = '\n'.join(key for key in data_sets)
    print(f'Data sets:\n{keys}\nPut in arg #1')
    sys.exit(1)

data_set = data_sets[sys.argv[1]]

# allowing for None end chars
if data_set['str-end-chars'] is not None:
    data_set['str-end-chars'] *= -1

with open(data_set['file-location']) as file:
    # for processing huge files
    csv.field_size_limit(sys.maxsize)
    # you can unpack a list: no tupling required here
    raw_data = list(csv.reader(file))
    print('raw_data\n')


@timer
def formatted_data_(raw_data):
    return [
        row[data_set['data-index']][
            data_set['str-start-chars']:data_set['str-end-chars']]
        for row in raw_data[1:]]


formatted_data = formatted_data_(raw_data)
print('formatted_data\n')

# mo county data pairs coords differently
if data_set == data_sets['mo-counties']:
    formatted_data = [
        (label, coords.replace(',', ' '))
        for label, coords in formatted_data
    ]


@timer
@vector()
def split_coords_(str):
    return str.split(' ')


split_coords = split_coords_(formatted_data)
print('split_coords\n')


# turn strings into floats by trimming off traiing characters if necessary
def float_recur(str, n=1):
    if n > 1000:     # Or else it causes stack overflow (???)
        return None  # Also good for debugging
    try:
        return float(str)
    except Exception:
        return float_recur(str[:-1], n=n + 1)


@timer
@vector()
def float_coords_(coords):
    return float_recur(coords)


float_coords = float_coords_(split_coords)
print('float_coords\n')


@timer
@vector(2)
def coord_pairs_(coords):
    enum = enumerate(coords)
    evens = (val for i, val in enum if not i % 2)
    odds = (val for i, val in enum if i % 2)
    return zip(evens, odds)


coord_pairs = coord_pairs_(float_coords)
print('coord_pairs\n')

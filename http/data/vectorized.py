import csv
import sys
import time
import matplotlib.pyplot as plt
from config import data_sets

try:
    data_set = data_sets[sys.argv[1]]
    if sys.argv[1] not in data_sets:
        raise IndexError
    if sys.argv[1] in ['-h', '-help', '--help']:
        raise IndexError
except IndexError as error:
    keys = '\n'.join(key for key in data_sets)
    print(f'Data sets:\n{keys}\nPut in arg #1')
    sys.exit(1)


def timer(f):
    """\
    Print the execution time of the wrapped function to console.
    """
    def decorator(*args, **kwargs):
        t = time.clock()
        result = f(*args, **kwargs)
        print('%.6f'%(time.clock() - t))
        return result
    return decorator


def restrict(index):
    """\
    Restrict the wrapped function to access a specific index of the wrapped
    function.
    """
    def decorated(f):
        def decorator(list, *args, **kwargs):
            return type(list)([
                *list[:index],
                f(list[index], *args, **kwargs),
                *list[index + 1:1],
            ])
        return decorator
    return decorated


def vector_2d(f):
    """\
    Perform the same operation on each element of a 2d list
    """
    def decorator(list, *args, **kwargs):
        return [f(item, *args, **kwargs) for item in list]
    return decorator


# allowing for None end chars
if data_set['str-end-chars'] is not None:
    data_set['str-end-chars'] *= -1

with open(data_set['file-location']) as file:
    # for processing huge files
    csv.field_size_limit(sys.maxsize)
    # you can unpack a list: no tupling required here

    @timer
    def raw_data_(file):
        return list(csv.reader(file))

    raw_data = raw_data_(file)
    print('raw_data\n')


@timer
def formatted_data_(raw_data):
    return [
        (
            row[data_set['label-index']],
            row[data_set['data-index']][
                data_set['str-start-chars']:data_set['str-end-chars']
            ]
        )
        for row in raw_data[1:]
    ]


formatted_data = formatted_data_(raw_data)
print('formatted_data\n')

# mo county data pairs coords differently
if data_set == data_sets['mo-counties']:
    formatted_data = [
        (label, coords.replace(',', ' '))
        for label, coords in formatted_data
    ]


# finally some functions
@timer
@vector_2d
@restrict(1)
def split_coords_(str):
    """\
    Split the str in position 1 for each element in the argument
    """
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
@vector_2d
@restrict(1)
def float_coords_(coords):
    """\
    """
    return [float_recur(coord) for coord in coords]


float_coords = float_coords_(split_coords)
print('float_coords\n')


@timer
@vector_2d
@restrict(1)
def coord_pairs_(coords):
    return [
        (coords[i], coords[i + 1])
        for i in range(len(coords))
        if not i % 2
    ]


coord_pairs = coord_pairs_(float_coords)
print('coord_pairs\n')


@timer
def boundaries_(coord_pairs):
    return [
        (label, zip(*coords))
        for label, coords in coord_pairs
    ]


boundaries = boundaries_(coord_pairs)
print('boundaries\n')


@timer
def plot_(boundaries):
    for label, boundary in boundaries:
        plt.plot(*boundary)


plot_(boundaries)
print('showing plot')
plt.show()
print('\ndone')

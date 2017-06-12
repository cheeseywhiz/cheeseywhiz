#!/usr/bin/env python3
import csv
import sys
import matplotlib.pyplot as plt

DATA_SETS = {
    'bay-area-zip-codes': {
        'file-location': 'sets/bay-area-zip-codes',
        'show-labels': True,
        'label-index': 3,
        'data-index': 1,
        'str-start-chars': 16,
        'str-end-chars': 3,
    },
    'idk': {
        'file-location': 'sets/idk',
        'show-labels': False,
        'label-index': 0,
        'data-index': 10,
        'str-start-chars': 10,
        'str-end-chars': 2,
    },
    'sf-zones': {
        'file-location': 'sets/sf-zones',
        'show-labels': False,
        'label-index': 0,
        'data-index': 5,
        'str-start-chars': 10,
        'str-end-chars': 2,
    },
    'ny-senate': {
        'file-location': 'sets/ny-senate',
        'show-labels': True,
        'label-index': 0,
        'data-index': 3,
        'str-start-chars': 16,
        'str-end-chars': 3,
    },
    'md-counties': {
        'file-location': 'sets/md-counties',
        'show-labels': True,
        'label-index': 0,
        'data-index': 1,
        'str-start-chars': 16,
        'str-end-chars': 3,
    },
}

try:
    sys.argv[1]
    if sys.argv[1] not in DATA_SETS:
        raise IndexError
except IndexError as error:
    keys = '\n'.join(key for key in DATA_SETS)
    print(f'Data sets:\n{keys}\nPut in arg #1')
    sys.exit(1)

data_set = DATA_SETS[sys.argv[1]]

with open(data_set['file-location']) as file:
    # for processing huge files
    csv.field_size_limit(sys.maxsize)
    # you can unpack a list: no tupling required here
    raw_data = list(csv.reader(file))
    print('read data')

# headers from data[0] so far
# strip MULTIPOLYGON ((( ))) from coordinates string
# remove headers row [0]
formatted_data = [
    (
        row[data_set['label-index']].capitalize(),
        row[data_set['data-index']][
            data_set['str-start-chars']:-data_set['str-end-chars']
        ]
    )
    for row in raw_data[1:]
]
print('formatted data')

# split up numbers to furthur work with
split_coords = [
    (label, coords_str.split(' '))
    for label, coords_str in formatted_data
]
print('split coords')


# turn strings into floats by trimming off traiing characters if necessary
def float_recur(str, n=1):
    if n > 1000:     # Or else it causes stack overflow (???)
        return None  # Also good for debugging
    try:
        return float(str)
    except Exception:
        return float_recur(str[:-1], n=n + 1)


float_coords = [
    (label, [float_recur(coord) for coord in coords_str])
    for label, coords_str in split_coords
]
print('turned coords into floats')


# throw pairs of consecutive lat/longs together in a single tuple
def combine(list):
    for i in range(len(list)):
        if not i % 2:
            yield list[i], list[i + 1]


coord_pairs = [
    (label, [i for i in combine(coords)])
    for label, coords in float_coords
]
print('paired coords')


# calculate the center of the area to place the label
def center(points: list):
    # filter out None values from combine() generator
    points = [
        (x, y)
        for x, y in points
        if not (x is None or y is None)
    ]

    def avg(list):
        return sum(list) / len(list)

    x, y = zip(*points)
    return avg(x), avg(y)


label_geom_center = [
    (label, coords, center(coords))
    for label, coords in coord_pairs
]
print('calculated centers')

# convert pairs of coordinates into lists of lats and longs
boundaries = [
    (label, zip(*coords), center)
    for label, coords, center in label_geom_center
]
print('made lat/long lists')

fontdict = {
    'family': 'Monospace',
    'color': 'black',
    'weight': 'normal',
    'size': 8,
}

# plot the data
for label, boundary, center in boundaries:
    plt.plot(*boundary)
    if data_set['show-labels']:
        plt.text(*center, label, fontdict=fontdict)

print('showing plot')
plt.show()
print('done')

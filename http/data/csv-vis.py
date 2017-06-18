#!/usr/bin/env python3
import csv
import sys
import matplotlib.pyplot as plt
from config import data_sets, fontdict

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
    print('raw_data')

# headers from data[0] so far
# strip MULTIPOLYGON ((( ))) from coordinates string
# remove headers row [0]
formatted_data = [
    (
        row[data_set['label-index']].capitalize(),
        row[data_set['data-index']][
            data_set['str-start-chars']:data_set['str-end-chars']
        ]
    )
    for row in raw_data[1:]
]
print('formatted_data')

# mo county data pairs coords differently
if data_set == data_sets['mo-counties']:
    formatted_data = [
        (label, coords.replace(',', ' '))
        for label, coords in formatted_data
    ]

# split up numbers to furthur work with
split_coords = [
    (label, coords_str.split(' '))
    for label, coords_str in formatted_data
]
print('split_coords')


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
print('float_coords')


# throw pairs of consecutive lat/longs together in a single tuple
def combine(list):
    for i in range(len(list)):
        if not i % 2:
            yield list[i], list[i + 1]


coord_pairs = [
    (label, [i for i in combine(coords)])
    for label, coords in float_coords
]
print('coord_pairs')


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
print('label_geom_center')

# convert pairs of coordinates into lists of lats and longs
boundaries = [
    (label, zip(*coords), center)
    for label, coords, center in label_geom_center
]
print('boundaries')

# plot the data
for label, boundary, center in boundaries:
    plt.plot(*boundary)
    if data_set['show-labels']:
        plt.text(*center, label, fontdict=fontdict)

print('showing plot')
plt.show()
print('done')

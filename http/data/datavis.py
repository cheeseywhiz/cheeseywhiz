#!/usr/bin/env python3
"""\
Plot boundaries from public data sets
"""
import matplotlib.pyplot as plt
from static import JsonVis

# organize different configurations for different data sets in order to make
# quick changes
data_sets = {
    'chicago': {
        'url': '''https://data.cityofchicago.org/api/views/nvke-umup/rows.json\
?accessType=DOWNLOAD''',
        'mapping_proxy_index': 9,
    },
    'montgomery-md': {
        'url': '''https://data.montgomerycountymd.gov/api/views/e8ub-75qc/rows\
.json?accessType=DOWNLOAD''',
        'mapping_proxy_index': 9,
    },
    'NYPD': {
        'url': '''https://data.cityofnewyork.us/api/views/5rqd-h5ci/rows.json?\
accessType=DOWNLOAD''',
        'mapping_proxy_index': 10,
    },
}

DATA_SET = data_sets['NYPD']

raw_data = JsonVis().download(DATA_SET['url']).data

# trim coordinates out of entire set
MAPPING_PROXY = [i[DATA_SET['mapping_proxy_index']] for i in raw_data['data']]

# trim the labels in the data
single_str = [i[16:-3] for i in MAPPING_PROXY]

# split put the numbers to further work with
coords_str = [i.split(' ') for i in single_str]


# turn strings into floats by trimming off traiing characters if necessary
def float_recur(str, n=1):
    if n > 1000:     # Or else it causes stack overflow (???)
        return None  # Also good for debugging
    try:
        return float(str)
    except Exception:
        return float_recur(str[:-1], n=n + 1)


coord_floats = [[float_recur(i) for i in line] for line in coords_str]


# throw pairs of lat/longs together in a single tuple
def combine(list):
    for i in range(len(list)):
        if not i % 2:
            yield list[i], list[i + 1]


coord_tuples = [[i for i in combine(line)] for line in coord_floats]

# convert coordinate tuples into lat lists and long lists
boundaries = [list(zip(*line)) for line in coord_tuples]

# plot the data
for boundary in boundaries:
    plt.plot(*boundary)

plt.show()

#!/usr/bin/env python3
from album_match import *
import base64
import lzma
import pickle

PROCESSES = [
    (lambda x: pickle.dumps(x), lambda x: pickle.loads(x)),
    (lambda x: lzma.compress(x), lambda x: lzma.decompress(x)),
    (lambda x: base64.b64encode(x), lambda x: base64.b64decode(x)),
]

def encode(obj):
    for (encode_step, _) in PROCESSES:
        obj = encode_step(obj)

    return obj


def decode(obj):
    for (_, decode_step) in PROCESSES[::-1]:
        obj = decode_step(obj)

    return obj

sift = cv.SIFT_create()
library = get_library('album-covers-original', sift)
pickles_stats = {}

for fname, (_, _, _, descriptor) in library.items():
    save_descriptor = descriptor
    descriptor = encode(descriptor)
    pickles_stats[fname] = len(descriptor)
    descriptor = decode(descriptor)
    if not np.array_equal(descriptor, save_descriptor):
        raise RuntimeError

pp(pickles_stats)

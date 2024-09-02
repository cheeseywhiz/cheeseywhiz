#!/usr/bin/env python3
# https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html
import os
import pdb
import sys
import time
import cv2 as cv
import numpy as np
from pprint import pprint as pp
from statistics import mean
import functools

DEBUG = False
IM_WIDTH = 900


def imshow(img):
    cv.imshow('album_match', img)
    key = cv.waitKey(0)
    print(f'key {key} {chr(key)!r} pressed')
    cv.destroyAllWindows()


def imread(fname, resize_width=None):
    img = cv.imread(fname)

    if resize_width is not None:
        (h, w) = img.shape[:2]
        aspect_ratio = h / w
        new_height = int(resize_width * aspect_ratio)
        img = cv.resize(img, (resize_width, new_height))

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img, gray


def get_library(folder, feature_detector, resize_width=None):
    library = {} # fname: (img, gray, keypoints, descriptor)

    for fname in os.listdir(folder):
        img, gray = imread(f'{folder}/{fname}', resize_width)
        keypoints, descriptor = feature_detector.detectAndCompute(gray, None)
        library[fname] = img, gray, keypoints, descriptor

    return library


def debug(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'Exception: {e!r}')
            pdb.post_mortem(sys.exc_info()[2])
            raise

    return wrapper


@debug
def main(argv):
    global DEBUG
    if '--debug' in argv:
        DEBUG = True

    sift = cv.SIFT_create()

    library = get_library('album-covers-original', sift)
    # assume query album will take up about 2/3 of the query picture
    queries = get_library('queries', sift, resize_width=900 * 3 // 2)

    for query_fname in queries:
        query_image(sift, library, queries, query_fname)

    pp(queries)


def query_image(orb, library, queries, query_fname):
    q_img, q_gray, q_kp, query_descriptor = queries[query_fname]
    all_matches = {}

    for library_fname, (l_img, _, l_kp, library_descriptor) in library.items():
        matcher = cv.BFMatcher()
        matches = matcher.knnMatch(library_descriptor, query_descriptor, k=2)
        matches = [
            [m]
            for m,n in matches
            if m.distance < 0.75 * n.distance
        ]

        if DEBUG:
            matches_img = cv.drawMatchesKnn(l_img, l_kp, q_img, q_kp, matches, None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            imshow(matches_img)

        matches_stat = len(matches)
        all_matches[library_fname] = matches_stat

    winner = sorted(all_matches.items(), key=lambda p: p[1])[-1] if library else None
    queries[query_fname] = winner, all_matches


if __name__ == '__main__':
    main(sys.argv)

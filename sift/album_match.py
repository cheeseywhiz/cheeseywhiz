#!/usr/bin/env python3
# https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html
import os
import sys
import time
import cv2 as cv
import numpy as np
from pprint import pprint as pp
from statistics import mean


def imshow(img):
    cv.imshow('album_match', img)
    key = cv.waitKey(0)
    print(f'key {key} {chr(key)!r} pressed')
    cv.destroyAllWindows()


def imread(fname):
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img, gray


def get_library(folder, feature_detector):
    library = {} # fname: (img, gray, keypoints, descriptor)

    for fname in os.listdir(folder):
        img, gray = imread(f'{folder}/{fname}')
        keypoints, descriptor = feature_detector.detectAndCompute(gray, None)
        library[fname] = img, gray, keypoints, descriptor

    return library


def main(argv):
    sift = cv.SIFT_create()

    library = get_library('album-covers-original', sift)
    queries = get_library('queries', sift)

    for query_fname in queries:
        do_query(sift, library, queries, query_fname)

    pp(queries)


def do_query(orb, library, queries, query_fname):
    q_img, q_gray, q_kp, query_descriptor = queries[query_fname]
    all_matches = {}

    for library_fname, (_, _, _, library_descriptor) in library.items():
        matcher = cv.BFMatcher()
        matches = matcher.knnMatch(library_descriptor, query_descriptor, k=2)
        matches = mean(
            m.distance
            for m,n in matches
            if m.distance < 0.75 * n.distance
        )
        all_matches[library_fname] = matches

    queries[query_fname] = q_img, q_gray, query_descriptor, all_matches


if __name__ == '__main__':
    main(sys.argv)

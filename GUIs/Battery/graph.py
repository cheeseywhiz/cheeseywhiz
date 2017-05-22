#!/usr/bin/python3
"""Provides continuous output of battery level data."""
from time import time
from matplotlib import pyplot as plt
import battery


def loop():
    """pass."""
    old_percentage = battery.percentage()
    old_time = time.time()
    while True:
        new_percentage = battery.percentage()
        new_time = time()
    pass
    while True: pass

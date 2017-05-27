#!/usr/bin/python3
import time
import matplotlib.pyplot as plt
import battery


def loop(tick, event, max_loop=0):
    """None loop(float tick, function event, int max_loop=0)
    Call <event>() a maximum of <max_loop> times if the battery
    percentage has changed and check if has changed every <tick> seconds.
    Set max_size to 0 to run indefinitely."""
    if not max_loop:
        from sys import maxsize
        max_loop = maxsize
        del maxsize

    t0 = time.time()
    percentage0 = battery.percentage()
    n = 1

    try:
        event()
        while n < max_loop:
            t1 = time.time()
            if t1 - t0 <= tick:
                t0 = t1
                percentage1 = battery.percentage()
                if percentage0 != percentage1:
                    percentage0 = percentage1
                    n += 1
                    event()
    except KeyboardInterrupt as error:
        print(str(error), 'User interrupted.')
    else:
        print('Successfully looped.')


def printtime():
    print(time.time(), battery.percentage())

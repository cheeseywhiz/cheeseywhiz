#!/usr/bin/python3
import sys
import os
import time

t0 = time.clock()


def filename():
    if 'C:\\' not in sys.argv[1]:
        file = "'" + os.getcwd() + "/" + str(sys.argv[1]) + "'"
        return file.replace('\\', '/')
    else:
        return ("'" + str(sys.argv[1]) + "'").replace('\\', '/')


if __name__ == '__main__':
    try:
        arg = sys.argv[1]
    except Exception as err:
        arg = '-h'
    if arg == '-h':
        with open('help') as file:
            print(file.read())
        sys.exit()
    else:
        with open(arg, 'r') as file:
            exec((file.read()).replace('THIS_FILEPATH', filename()))
    print(time.clock() - t0)

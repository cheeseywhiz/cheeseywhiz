#!/usr/bin/python3
from subprocess import check_output
def str_cmd(string):
    return check_output(string.split(),shell=True).decode('utf-8')

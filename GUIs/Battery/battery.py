#!/usr/bin/python3
"""Short API to access battery data."""
from subprocess import call


def info():
    """Dictionary of battery information."""
    call('batteryinfo.sh')
    with open('pipe') as file:
        info = file.read().split('\n')
    # Inner loop: remove extra whitespace from line
    # Outer loop: do this for each line
    info = [[letter
             for letter in line.split(' ')
             if letter != ''] for line in info]

    def line(list):
        """Turn split string into formatted tuple.

        line(list) -> tuple(str variable, str value)."""
        # leave variable i on element that has colon as last character
        for i, word in enumerate(list):
            if word[-1] == ':':
                i += 1
                break
        else:
            i = 0
        # Join words together with spaces while removing colon
        return ' '.join(list[:i])[:-1], ' '.join(list[i:])
    return dict(line(elem) for elem in info)


def percentage():
    """Battery charge percentage."""
    energy = info()
    return float(energy['energy'][:-3]) / float(energy['energy-full'][:-3])


if __name__ == '__main__':
    print(info())
    print(percentage())

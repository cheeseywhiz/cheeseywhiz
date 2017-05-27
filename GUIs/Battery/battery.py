#!/usr/bin/python3
import subprocess
import decorators


def info():
    """Dictionary of battery information:

    native-path
    vendor
    model
    serial
    power supply
    updated
    present
    rechargeable
    state
    energy
    energy-empty
    energy-full
    energy-full-design
    energy-rate
    voltage
    time to empty
    percentage
    capacity
    technology"""
    subprocess.call('batteryinfo.sh')

    with open('pipe') as file:
        info = file.read().split('\n')

    # Remove whitespace on each line
    # Just individual words left
    info[:] = [[letter
                for letter in line.split(' ')
                if letter != '']
               for line in info]

    @decorators.vector_1d
    def info_format(line):
        # leave variable i on element that has colon as last character
        # variable i decides which words are assigned to the stat or the val
        for i, word in enumerate(line, start=1):
            if word[-1] == ':':
                break
        else:
            i = 0

        # Join words together with spaces while removing colon (last char)
        return ' '.join(line[:i])[:-1], ' '.join(line[i:])

    whitelist = ['native-path', 'vendor', 'model', 'serial', 'power supply',
                 'updated', 'present', 'rechargeable', 'state', 'energy',
                 'energy-empty', 'energy-full', 'energy-full-design',
                 'energy-rate', 'voltage', 'time to empty', 'percentage',
                 'capacity', 'technology']
    info = {stat: val
            for stat, val in info_format(info)
            if stat in whitelist}
    info['percentage'] = str(100
                             * float(info['energy'][:-3])
                             / float(info['energy-full'][:-3])) + '%'
    return info


if __name__ == '__main__':
    import pprint
    pprint.pprint(info())

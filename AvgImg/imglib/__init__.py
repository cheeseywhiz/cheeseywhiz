import os as _os
import sys as _sys
from matplotlib import pyplot as _plt


def load_global(inst):
    global g
    g = inst


class ImageIter:
    def __init__(self, fname=None, px_map=None):
        if fname is not None:
            self.px_map = _plt.imread(fname)
        elif px_map is not None:
            self.px_map = px_map

        self.width, self.height, self.color_len = self.px_map.shape

    def __getitem__(self, row):
        return self.px_map[row]

    def __iter__(self):
        return (
            (row, col, self.__getitem__(row)[col])
            for row in range(self.width)
            for col in range(self.height)
        )


def colormaps():
    try:
        _plt.get_cmap('')
    except ValueError as error:
        cmaps_str = sorted(str(error).split(':')[1][1:].split(', '))

    row_length = 0
    row = []
    rows = []
    for cmap in cmaps_str:
        row_length += len(cmap + ', ')
        if row_length < 80:
            row.append(cmap)
        else:
            rows.append(
                ', '.join(row) + ','
            )
            row.clear()
            row.append(cmap)
            row_length = len(cmap + ', ')

    return '\n'.join(rows)[:-1]


def get_flag(argv, flag):
    for option in argv:
        if option.startswith(flag):
            break
    else:
        return

    argv.remove(option)
    return option.split('=')[1]


def parse_argv(argv, good_flags):
    """\
argv is the list of arguments passed into the command line.
good_flags is a list of expected flags to parse and is used to build the
initial structure.

Return a dictionary with the following structure:
    {
        '-flag1': value,
        '-flag2': value,
        '+flag3': value,
        ...,
        'positional' : ('python3', ...)  # e.g.
    }

Each flag's value starts off as False. If the flag was not specified, the value
in the dictionary stays as False. If the flag was specified with an option,
(e.g. -f=123) the option (e.g. 123) is stored under the flag in the dictionary.
If the flag was specified without an option (e.g. -h), None is stored in the
dictionary.

'positional' holds user-specified arguments that did not start with + or -
while retaining the order they were specified in the command.\
"""
    options = {
        key: False
        for key in good_flags
    }
    positional = []

    for arg in argv:
        if arg[0] in ['-', '+']:
            if '=' in arg:
                arg, value = arg.split('=')
                options[arg] = value
            else:
                options[arg] = None
            if arg not in good_flags:
                _sys.exit(f'Unknown flag {arg}')
        else:
            positional.append(arg)

    options['positional'] = tuple(positional)
    return options


def trim(argv):
    msgs = []
    verbose = False
    good_flags = [
        '-h', '-hc', '-avg', '-c', '-i', '-o', '+o', '-s', '-v',
    ]
    flags = parse_argv(argv, good_flags)

    if flags['-h'] is None or len(argv) == 1:
        print(g.__DOC__)
        _sys.exit(0)

    if flags['-hc'] is None:
        print(colormaps())
        _sys.exit(0)

    if flags['-avg']:
        avg_func_name = flags['-avg']
        msgs.append(f'With {avg_func_name} as average')
    elif flags['-avg'] is None:
        _sys.exit('Missing required -avg option')
    elif not flags['-avg']:
        avg_func_name = 'mean'

    if flags['-c']:
        cmap_name = flags['-c']
        g.CMAP = cmap_name
        g.GRAYSCALE = True
        msgs.append(f'With color map {cmap_name}')
    elif flags['-c'] is None:
        _sys.exit('Missing required -c option')
    elif not flags['-c']:
        # Defaults set in global
        pass

    if flags['-i'] is None:
        g.INVERT = not g.INVERT
        msgs.append(f'{"With" if g.INVERT else "Without"} inverted colors')
    elif not flags['-i']:
        # Default set in global
        pass

    if flags['-o']:
        fname = _os.path.abspath(_os.path.expanduser(flags['-o']))
        msgs.append(f'Output image at {fname}')
    elif flags['-o'] is None:
        _sys.exit('Missing required output filename')
    elif not flags['-o']:
        fname = _os.path.abspath('output.png')

    if flags['+o'] is None:
        fname = '/tmp/output.png'
    elif not flags['+o']:
        pass

    if flags['-s']:
        exit_func_name = flags['-s']
        msgs.append(f'Opening with {exit_func_name}')
    elif flags['-s'] is None:
        _sys.exit('Missing required -s option')
    elif not flags['-s']:
        exit_func_name = 'done'

    if flags['-v'] is None:
        verbose = True
        msgs.insert(0, 'Parsed options:')

    avg_func = getattr(_Avg, avg_func_name)
    exit_func = getattr(_Exit, exit_func_name)

    try:
        given_dir = flags['positional'][1]
    except IndexError:
        _sys.exit('Missing required source directory')

    imgs_dir = _os.path.abspath(_os.path.expanduser(given_dir))
    msgs.append(f'Averaging {imgs_dir}/*')

    if verbose:
        print(msgs[0])
        for msg in msgs[1:]:
            print(4 * ' ' + msg)

    return imgs_dir, avg_func, fname, exit_func


def _average_f(f):
    def if_invert(num):
        if g.INVERT:
            return int(256 - num)
        else:
            return int(num)

    def if_grayscale(nums):
        if g.GRAYSCALE:
            return sum(nums) / len(nums)
        else:
            return nums

    def decorated_f(tuples, *args, **kwargs):
        def avg(tuples, i):
            return f([tup[i] for tup in tuples], *args, **kwargs)

        return if_grayscale([
            if_invert(avg(tuples, i))
            for i in range(len(tuples[0]))
        ])

    return decorated_f


class _Avg:
    @staticmethod
    @_average_f
    def mean(nums):
        return sum(nums) / len(nums)

    @staticmethod
    @_average_f
    def median(nums):
        return sorted(nums)[len(nums) // 2]

    @staticmethod
    @_average_f
    def max(nums):
        return max(nums)

    @staticmethod
    @_average_f
    def min(nums):
        return min(nums)


class _Exit:
    @staticmethod
    def feh(fname=None, **kwargs):
        _Exit.done()
        from subprocess import run
        run(f'feh {fname}', shell=True)

    @staticmethod
    def mpl(array=None, **kwargs):
        _Exit.done()
        _plt.imshow(array, cmap=g.CMAP)
        _plt.show()

    @staticmethod
    def done(**kwargs):
        pass  # print('Done')

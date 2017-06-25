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
        cmaps_list1 = sorted(str(error).split(':')[1][1:].split(', '))

    row_length = 0
    row = []
    rows = []
    for cmap in cmaps_list1:
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

    return '\n'.join(rows)


def trim(argv):
    msgs = []
    verbose = False
    flags = [
        '-h', '-hc', '-avg', '-c', '-g', '-i', '-o', '+o', '-s', '-v'
    ]

    for flag in argv:
        if flag.startswith('-') or flag.startswith('+'):
            if flag not in flags:
                _sys.exit(f'Unknown flag {flag}')

    if '-h' in argv:
        print(g.__DOC__)
        _sys.exit(0)

    if '-hc' in argv:
        print(colormaps())
        _sys.exit(0)

    if '-avg' in argv:
        avg_flag = argv.index('-avg')
        argv.pop(avg_flag)
        try:
            avg_func_name = argv.pop(avg_flag)
        except IndexError:
            _sys.exit('Missing required -avg option')
        avg_func = getattr(_Avg, avg_func_name)
        msgs.append(f'With {avg_func_name} as average')
    else:
        avg_func = getattr(_Avg, 'mean')
        msgs.append('With mean as average')

    if '-c' in argv:
        c_flag = argv.index('-c')
        argv.pop(c_flag)
        try:
            cmap = argv.pop(c_flag)
        except IndexError:
            _sys.exit('Unknown -c option')
        g.CMAP = cmap
        msgs.append(f'With cmap {cmap}')

    if '-g' in argv:
        g_flag = argv.index('-g')
        argv.pop(g_flag)
        g.GRAYSCALE = True
        msgs.append('With grayscale')

    if '-i' in argv:
        i_flag = argv.index('-i')
        argv.pop(i_flag)
        g.INVERT = not g.INVERT
        msgs.append(f'{"With" if g.INVERT else "Without"} inverted colors')

    tmp_fname = '/tmp/output.png'
    if '-o' in argv:
        o_flag = argv.index('-o')
        argv.pop(o_flag)
        try:
            fname = _os.path.abspath(argv.pop(o_flag))
        except IndexError:
            _sys.exit('Missing required output filename')
    elif '+o' in argv:
        o_flag = argv.index('+o')
        argv.pop(o_flag)
        msgs.append('Temp ouput file')
        fname = tmp_fname
    else:
        cwd = _os.getcwd()
        fname = _os.path.join(cwd, 'output.png')
    if fname != tmp_fname:
        msgs.append(f'Saving to {fname}')

    if '-s' in argv:
        s_flag = argv.index('-s')
        argv.pop(s_flag)
        try:
            exit_func_name = argv.pop(s_flag)
        except IndexError:
            _sys.exit('Missing required -s option')
        exit_func = getattr(_Exit, exit_func_name)
        msgs.append(f'Showing output with {exit_func_name}')
    else:
        exit_func = getattr(_Exit, '_done')
        msgs.append('Not showing output')

    if '-v' in argv:
        v_flag = argv.index('-v')
        argv.pop(v_flag)
        verbose = True
        msgs.insert(0, 'Parsed options:')

    # Once each flag is pop()'d, the no-flag source dir should be the last item
    # in the list.
    imgs_dir = _os.path.abspath(argv.pop())
    msgs.append(f'Averaging {imgs_dir}/*')
    # we pop()'d the called command
    if len(argv) == 0:
        _sys.exit('Missing required source directory')

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
        _Exit._done()
        from subprocess import run
        run(f'feh {fname}', shell=True)

    @staticmethod
    def mpl(array=None, **kwargs):
        _Exit._done()
        _plt.imshow(array, cmap=g.CMAP)
        _plt.show()

    @staticmethod
    def _done(**kwargs):
        pass  # print('Done')

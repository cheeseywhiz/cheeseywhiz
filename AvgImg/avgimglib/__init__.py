import os as _os
import sys as _sys


def load_global(inst):
    global g
    g = inst


def average_f(f):
    def if_invert(num):
        if g.INVERT:
            return int(255 - num)
        else:
            return int(num)

    def if_grayscale(nums):
        if g.GRAYSCALE:
            avg = sum(nums) / len(nums)
            return avg, avg, avg
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


class Avg:
    @staticmethod
    @average_f
    def mean(nums):
        return sum(nums) / len(nums)

    @staticmethod
    @average_f
    def median(nums):
        return sorted(nums)[len(nums) // 2]

    @staticmethod
    @average_f
    def max(nums):
        return max(nums)

    @staticmethod
    @average_f
    def min(nums):
        return min(nums)


class Exit:
    @staticmethod
    def feh(fname=None, **kwargs):
        Exit._done()
        from subprocess import run
        run(f'feh {fname}', shell=True)

    @staticmethod
    def mpl(array=None, **kwargs):
        Exit._done()
        from matplotlib import pyplot as plt
        plt.imshow(array, cmap=g.CMAP)
        plt.show()

    @staticmethod
    def _done(**kwargs):
        print('Done')


def trim(argv):
    msgs = []
    verbose = False

    if '-h' in argv:
        print(g.__DOC__)
        _sys.exit(0)

    if '-avg' in argv:
        avg_flag = argv.index('-avg')
        argv.pop(avg_flag)
        try:
            avg_func_name = argv.pop(avg_flag)
        except IndexError:
            _sys.exit('Missing required -avg option')
        avg_func = getattr(Avg, avg_func_name)
        msgs.append(f'With {avg_func_name} as average')
    else:
        avg_func = Avg.mean
        msgs.append('With mean as average')

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
        exit_func = getattr(Exit, exit_func_name)
        msgs.append(f'Showing output with {exit_func_name}')
    else:
        exit_func = getattr(Exit, '_done')
        msgs.append('Not showing output')

    if '-v' in argv:
        verbose = True
        v_flag = argv.index('-v')
        argv.pop(v_flag)
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

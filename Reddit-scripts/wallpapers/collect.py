#!/home/cheese/cheeseywhiz/Reddit-scripts/wallpapers/bin/python
import sys
from collections import namedtuple as _namedtuple
from functools import partial, wraps
from pathlib import Path
from random import shuffle
from requests import get as _get
from subprocess import Popen, DEVNULL
from time import sleep
from urllib.parse import urlparse

REDDIT_LINK = 'https://www.reddit.com/r/earthporn/hot/.json?limit=10'


def _rich_message(*values, beginning=None, label=None, **print_kwargs):
    if beginning is None:
        beginning = Path(__file__).name + ': '

    print_func = partial(partial(print, flush=True), **print_kwargs)
    print_label = partial(print_func, end='')

    print_label(beginning)

    if label is not None:
        print_label(label)

    print_func(*values)


log = partial(_rich_message, file=sys.stderr)
error = partial(_rich_message, label='Error: ', file=sys.stderr)


def ping(host):
    return not Popen(
        ['ping', '-c 1', '-w 1', host],
        stdout=DEVNULL, stderr=DEVNULL,
    ).wait()


@wraps(_get)
def get(*args, **kwargs):
    log(f'Requesting {args[0]} ... ', end='')
    res = partial(
        _get,
        headers={'User-Agent': 'u/cheeseywhiz'},
    )(*args, **kwargs)
    log(res.status_code, res.reason, beginning='')
    return res


def _named_tuple_wrapper(func, type_name, field_names, *, verbose=False,
                         rename=False, module=None):
    """\
    Wrap a function by turning its result into a named tuple.
    """
    if type_name is None:
        type_name = f'{func.__name__}_result'

    result_tuple = _namedtuple(
        type_name, field_names, verbose=verbose, rename=rename, module=module)

    @wraps(func)
    def wrapped_func(*func_args, **func_kwargs):
        result = func(*func_args, **func_kwargs)
        return result_tuple._make(result)

    return wrapped_func


def namedtuple(*field_names, type_name=None, verbose=False, rename=False,
               module=None):
    """\
    Decorator factory to turn _named_tuple_wrapper into a proper decorator that
    has a similar signature to collections.namedtuple but is more decorator
    friendly.
    """
    return partial(
        _named_tuple_wrapper,
        type_name=type_name, field_names=field_names, verbose=verbose,
        rename=rename, module=module)


def random_map(func, *iterables):
    if len(iterables) == 1:
        args = zip(iterables[0])
    else:
        args = zip(*iterables)

    args = list(args)
    shuffle(args)

    return map(func, *zip(*args))


@namedtuple('succeeded', 'status', 'url', 'path')
def download(dir, url):
    re = get(url)

    error_msg = None
    type_ = re.headers['content-type']
    if not type_.startswith('image'):
        error_msg = 'not an image'
    if type_.endswith('gif'):
        error_msg = 'is a .gif'
    if 'removed' in re.url:
        error_msg = 'appears to be removed'
    if error_msg:
        return False, error_msg, url, None

    new_path = dir / urlparse(re.url).path.split('/')[-1]
    if new_path.exists():
        return True, 'Already downloaded', url, new_path
    with new_path.open('wb') as file:
        file.write(re.content)
    return True, 'Collected new image', url, new_path


def main(argv):
    max_seconds = 60
    seconds_wait = 5

    for n_try in range(max_seconds // seconds_wait):
        if not ping('8.8.8.8'):
            error('Connection not found')
            sleep(seconds_wait)
        elif n_try:
            log('Connection found')
            break
        else:
            break
    else:  # no break; really no internet connection
        error('Too many tries')
        return 1

    try:
        save_dir = Path(argv[1])
    except IndexError:
        save_dir = Path('/tmp/wal')

    save_dir.mkdir(exist_ok=True)

    urls = (
        post['data']['url']
        for post in get(REDDIT_LINK).json()['data']['children'])

    download_ = partial(download, save_dir)

    for res in random_map(download_, urls):
        if not res.succeeded:
            error(res.status, res.url, sep=': ')
            continue
        else:
            log(res.status)
            log(res.path, label='Output: ')
            print(res.path)
            return 0
    else:  # no break; did not succeed
        return 1


if __name__ == '__main__':
    main_return = main(sys.argv)

    if main_return:
        sys.exit(main_return)

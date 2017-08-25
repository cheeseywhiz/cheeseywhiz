#!/home/cheese/cheeseywhiz/Reddit-scripts/wallpapers/bin/python
import functools
import inspect
import subprocess
import sys
from pathlib import Path
from random import shuffle
from requests import get as _get
from time import sleep as _sleep
from urllib.parse import urlparse
import cache

REDDIT_LINK = 'https://www.reddit.com/r/earthporn/hot/.json?limit=10'
download_cache = cache.DownloadCache(Path.home() / '.cache/wal/collect.cache')

try:
    current_cache = download_cache.read()
except EOFError:
    current_cache = {}

_no_doc = list(functools.WRAPPER_ASSIGNMENTS)
_no_doc.remove('__doc__')


@functools.wraps(functools.partial, assigned=_no_doc)
def partial(func, *args, **kwargs):
    """partial(func, *args, **kwargs)
    functools.partial as a decorator for top level functions.
    Able to wrap itself with 0-2 yield statements where the second yields a
    function that takes the result as an argument"""
    partial_func = functools.partial(func, *args, **kwargs)
    func_sig = inspect.signature(partial_func)

    def decorator(wrapped):
        @functools.wraps(func)
        @functools.wraps(wrapped)
        def wrapper(*wargs, **wkwargs):
            func_generator = wrapped(*wargs, **wkwargs)

            if func_generator is not None:
                next(func_generator)

            result = partial_func(*wargs, **wkwargs)

            if func_generator is None:
                return result

            try:
                yield_func = next(func_generator)
                if yield_func is not None:
                    yield_func(result)
            finally:
                return result

        wrapper.__signature__ = func_sig
        wrapper.__qualname__ = wrapped.__qualname__

        return wrapper

    return decorator


def _rich_message(*values, beginning=None, label=None, sep=' ',
                  **print_kwargs):
    """{beginning}{label}{value}{sep}{value}{sep}{value}{end} > file"""
    if not __debug__:
        kwargs = {'beginning': beginning, 'label': label, 'sep': sep,
                  **print_kwargs}
        print('Called with', values, kwargs)

    print_func = functools.partial(
        functools.partial(print, flush=True),
        **print_kwargs)

    parts = [beginning, label]

    for i, value in enumerate(values, 1):
        parts.append(value)
        if i != len(values):
            parts.append(sep)

    final = ''.join(str(part) for part in parts if part is not None)
    print_func(final)


@partial(_rich_message, beginning=Path(__file__).name + ': ', file=sys.stderr)
def log(*args, **kwargs):
    pass


@partial(log, label='Error: ')
def error(*args, **kwargs):
    pass


def ping(host='8.8.8.8'):
    """Internet connection test"""
    return not subprocess.Popen(
        ['ping', '-c 1', '-w 1', host],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).wait()


@partial(_get, headers={'User-Agent': 'u/cheeseywhiz'})
def get(url, *args, **kwargs):
    yield log('Requesting', url, '...', end=' ')
    yield (lambda req: log(req.status_code, req.reason, beginning=''))


def random_map(func, *iterables):
    """Implement map() by sending in arguments in a random order"""
    if len(iterables) == 1:
        args = zip(iterables[0])
    else:
        args = zip(*iterables)

    args = list(args)
    shuffle(args)

    return map(func, *zip(*args))


@cache.cache(current_cache)
def download(url):
    """Download an image and return cache.DownloadResult with relevant info"""
    req = get(url)

    error_msg = None
    type_ = req.headers['content-type']
    if not type_.startswith('image'):
        error_msg = 'Not an image'
    if type_.endswith('gif'):
        error_msg = 'Is a .gif'
    if 'removed' in req.url:
        error_msg = 'Appears to be removed'
    if error_msg:
        return cache.DownloadResult(False, error_msg, url, None, None)

    fname = urlparse(req.url).path.split('/')[-1]
    return cache.DownloadResult(
        True, 'Collected new image', url, fname, req.content)


def write_image(download_result, path):
    """Write an image to disk given a download() response and a full path"""
    path = Path(path)

    if path.exists():
        return download_result._replace(status='Already downloaded')

    with path.open('wb') as file:
        file.write(download_result.content)

    return download_result


def main(_, save_dir=None):
    max_seconds = 60
    seconds_wait = 5

    for n_try in range(max_seconds // seconds_wait):
        if not ping():
            error('Connection not found')
            _sleep(seconds_wait)
        elif n_try:
            log('Connection found')
            break
        else:
            break
    else:  # no break; really no internet connection
        error('Too many tries')
        return 1

    if save_dir is None:
        save_dir = '/tmp/wal'

    save_dir = Path(save_dir)

    save_dir.mkdir(exist_ok=True)

    urls = (
        post['data']['url']
        for post in get(REDDIT_LINK).json()['data']['children'])

    for res in random_map(download, urls):
        if not res.succeeded:
            error(res.status, res.url, sep=': ')
            continue
        else:
            path = save_dir / res.fname
            print(path)
            res = write_image(res, path)
            log(res.url, label='Success: ')
            log(res.status)
            log(path, label='Output: ')
            return 0
    else:  # no break; did not succeed
        error('Could not find image')
        return 1


if __name__ == '__main__':
    try:
        main_return = main(*sys.argv)
    finally:
        download_cache.write(download.cache)

    if main_return:
        sys.exit(main_return)

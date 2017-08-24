#!/home/cheese/cheeseywhiz/Reddit-scripts/wallpapers/bin/python
import sys
from functools import partial, wraps
from pathlib import Path
from random import shuffle
from requests import get as _get
from subprocess import Popen, DEVNULL
from time import sleep as _sleep
from urllib.parse import urlparse
import cache

REDDIT_LINK = 'https://www.reddit.com/r/earthporn/hot/.json?limit=10'
download_cache = cache.DownloadCache(Path.home() / '.cache/wal/collect.cache')

try:
    current_cache = download_cache.read()
except EOFError:
    current_cache = {}


def _rich_message(*values, beginning=None, label=None, sep=' ',
                  **print_kwargs):
    """{beginning}{label}{value}{sep}{value}{sep}{value}{end} > file"""
    print_func = partial(partial(print, flush=True), **print_kwargs)

    parts = [beginning, label]

    for i, value in enumerate(values, 1):
        parts.append(value)

        if i != len(values):
            parts.append(sep)

    final = ''.join(str(part) for part in parts if part is not None)
    print_func(final)


log = partial(
    _rich_message,
    beginning=Path(__file__).name + ': ',
    file=sys.stderr)
error = partial(log, label='Error: ')


def ping(host='8.8.8.8'):
    """Internet connection test"""
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
    re = get(url)

    error_msg = None
    type_ = re.headers['content-type']
    if not type_.startswith('image'):
        error_msg = 'Not an image'
    if type_.endswith('gif'):
        error_msg = 'Is a .gif'
    if 'removed' in re.url:
        error_msg = 'Appears to be removed'
    if error_msg:
        return cache.DownloadResult(False, error_msg, url, None, None)

    fname = urlparse(re.url).path.split('/')[-1]
    return cache.DownloadResult(
        True, 'Collected new image', url, fname, re.content)


def write_image(download_result, path):
    """Write an image to disk given a download() response and a full path"""
    if path.exists():
        return download_result._replace(status='Already downloaded')

    with path.open('wb') as file:
        file.write(download_result.content)

    return download_result


def main(argv):
    max_seconds = 60
    seconds_wait = 5

    for n_try in range(max_seconds // seconds_wait):
        if not ping('8.8.8.8'):
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

    try:
        save_dir = Path(argv[1])
    except IndexError:
        save_dir = Path('/tmp/wal')

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
            res = write_image(res, path)
            log(res.url, label='Success: ')
            log(res.status)
            log(path, label='Output: ')
            print(path)
            return 0
    else:  # no break; did not succeed
        error('Could not find image')
        return 1


if __name__ == '__main__':
    main_return = main(sys.argv)
    download_cache.write(download.cache)

    if main_return:
        sys.exit(main_return)

#!/home/cheese/cheeseywhiz/Reddit-scripts/wallpapers/bin/python
import functools
import random
import requests
import sys
from collections import namedtuple as _namedtuple
from pathlib import Path
from urllib.parse import urlparse

REDDIT_LINK = 'https://www.reddit.com/r/earthporn/hot/.json?limit=10'


def log(message):
    print(f'{Path(__file__).name}: {message}', file=sys.stderr)


@functools.wraps(requests.get)
def get(*args, **kwargs):
    log(f'Requesting {args[0]}')
    res = functools.partial(
        requests.get,
        headers={'User-Agent': 'u/cheeseywhiz'}
    )(*args, **kwargs)
    log(f'{res.status_code} {res.reason}')
    return res


def _named_tuple_wrapper(func, type_name, field_names, *, verbose=False,
                         rename=False, module=None):
    """\
    Wrap a function to turn its result into a named tuple.
    """
    if type_name is None:
        type_name = f'{func.__name__}_result'

    result_tuple = _namedtuple(
        type_name, field_names, verbose=verbose, rename=rename, module=module)

    @functools.wraps(func)
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
    return functools.partial(
        _named_tuple_wrapper,
        type_name=type_name, field_names=field_names, verbose=verbose,
        rename=rename, module=module)


def random_map(func, *iterables):
    if len(iterables) == 1:
        args = zip(iterables[0])
    else:
        args = zip(*iterables)

    args = list(args)
    random.shuffle(args)

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
    try:
        save_dir = Path(argv[1])
    except IndexError:
        save_dir = Path('/tmp/wal')

    save_dir.mkdir(exist_ok=True)

    urls = (
        post['data']['url']
        for post in get(REDDIT_LINK).json()['data']['children'])

    download_ = functools.partial(download, save_dir)

    for res in random_map(download_, urls):
        if not res.succeeded:
            log(f'Error: {res.status}: {res.url}')
            continue
        else:
            log(res.status)
            log(f'Output: {res.path}')
            print(res.path)
            break
    else:  # no break
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

#!/home/cheese/cheeseywhiz/Reddit-scripts/wallpapers/bin/python
import functools
import random
import requests
import subprocess
import sys
from collections import namedtuple as _namedtuple
from pathlib import Path
from urllib.parse import urlparse

get = functools.partial(requests.get, headers={'User-Agent': 'u/cheeseywhiz'})
REDDIT_LINK = 'https://www.reddit.com/r/earthporn/hot/.json?limit=10'


def named_tuple_wrapper(wrapped, type_name, field_names, *, verbose=False,
                        rename=False, module=None):
    """\
    Wrap a function to turn its result into a named tuple.
    """
    if type_name is None:
        type_name = f'{wrapped.__name__}_result'

    result_tuple = _namedtuple(
        type_name, field_names, verbose=verbose, rename=rename, module=module)

    @functools.wraps(wrapped)
    def wrapper(*func_args, **func_kwargs):
        result = wrapped(*func_args, **func_kwargs)
        return result_tuple(*result)

    return wrapper


def namedtuple(*field_names, type_name=None, verbose=False, rename=False,
               module=None):
    """\
    Decorator factory to turn named_tuple_wrapper into a proper decorator that
    has a similar signature to collections.namedtuple but is more decorator
    friendly.
    """
    return functools.partial(
        named_tuple_wrapper,
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


def mktemp_d():
    return subprocess.Popen(
        ['mktemp', '-d'],
        stdout=subprocess.PIPE
    ).communicate()[0].decode()[:-1]


@namedtuple('succeeded', 'status', 'url', 'path')
def download(dir, url):
    re = get(url)

    type_ = re.headers['content-type']

    if (
        not type_.startswith('image')
        or type_.endswith('gif')
        or 'removed' in re.url
    ):  # sad face
        return False, 'not a still image', url, None

    new_path = dir / urlparse(re.url).path.split('/')[-1]

    if new_path.exists():
        return False, 'exists', url, None

    with new_path.open('wb') as file:
        file.write(re.content)

    return True, 'success', url, new_path


def main(argv):
    try:
        save_dir = Path(argv[1])
    except IndexError:
        save_dir = Path(mktemp_d())

    save_dir.mkdir(exist_ok=True)

    urls = [
        post['data']['url']
        for post in get(REDDIT_LINK).json()['data']['children']]

    download_ = functools.partial(download, save_dir)

    for res in random_map(download_, urls):
        if not res.succeeded:
            continue
        else:
            print(res.path)
            break
    else:  # no break
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

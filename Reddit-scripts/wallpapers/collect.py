#!/home/cheese/cheeseywhiz/Reddit-scripts/wallpapers/bin/python
import functools
import random
import requests
import subprocess
import sys
from pathlib import Path
from collections import namedtuple

get = functools.partial(requests.get, headers={'User-Agent': 'u/cheeseywhiz'})
REDDIT_LINK = 'https://www.reddit.com/r/earthporn/hot/.json?limit=10'


def mktemp_d():
    new_path = subprocess.Popen(
        ['mktemp', '-d'],
        stdout=subprocess.PIPE).communicate()[0].decode()

    return new_path[:-1]


def download(url, dir):
    Result = namedtuple('Result', ['status', 'url', 'path'])
    re = get(url)

    type_ = re.headers['content-type']

    if (
        not type_.startswith('image')
        or type_.endswith('gif')
        or 'removed' in re.url
    ):
        return Result('not a still image', url, None)

    new_path = dir / re.url.split('/')[-1]

    if new_path.exists():
        return Result('exists', url, None)

    with new_path.open('wb') as file:
        file.write(re.content)

    return Result('success', url, new_path)


def main(argv):
    try:
        save_dir = Path(argv[1])
    except IndexError:
        save_dir = Path(mktemp_d())
    save_dir.mkdir(exist_ok=True)
    urls = [
        post['data']['url']
        for post in get(REDDIT_LINK).json()['data']['children']]
    res = download(random.choice(urls), save_dir)
    print(res.path)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

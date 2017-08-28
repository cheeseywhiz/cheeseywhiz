"""Provides functions for downloading images"""
import pathlib
import random
import sys
import time
from urllib.parse import urlparse

import requests

from . import util
from . import cache
from .config import REDDIT_LINK, SAVE_DIR


def random_map(func, *iterables):
    """Implement map() by sending in arguments in a random order"""
    if len(iterables) == 1:
        args = zip(iterables[0])
    else:
        args = zip(*iterables)

    args = list(args)
    random.shuffle(args)

    return map(func, *zip(*args))


@util.partial(
    util.rich_message, beginning=pathlib.Path(__file__).name + ': ',
    file=sys.stderr)
def log(*args, **kwargs):
    pass


@util.partial(log, label='Error: ')
def error(*args, **kwargs):
    pass


@util.partial(requests.get, headers={'User-Agent': 'u/cheeseywhiz'})
def get(url, *args, **kwargs):
    yield log('Requesting', url, '...', end=' ')
    yield lambda req: log(req.status_code, req.reason, beginning='')


@cache.cache()
def download(url):
    """Download an image and return cache.DownloadResult with relevant info"""
    req = get(url)
    time_ = int(time.time())

    error_msg = None
    type_ = req.headers['content-type']
    if not type_.startswith('image'):
        error_msg = 'Not an image'
    if type_.endswith('gif'):
        error_msg = 'Is a .gif'
    if 'removed' in req.url:
        error_msg = 'Appears to be removed'
    if error_msg:
        return cache.DownloadResult(url, time_, False, error_msg, None, None)

    fname = urlparse(req.url).path.split('/')[-1]
    return cache.DownloadResult(
        url, time_, True, 'Collected new image', fname, req.content)


def write_image(download_result, path):
    """Write an image to disk given a download() response and a full path"""
    path = pathlib.Path(path)

    if path.exists():
        return download_result._replace(status='Already downloaded')

    with path.open('wb') as file:
        file.write(download_result.content)

    return download_result


def collect(save_dir=None, url=None):
    """Download a random image from a Reddit .json url and save it in the given
    folder path."""
    if save_dir is None:
        save_dir = SAVE_DIR
    if url is None:
        url = REDDIT_LINK

    max_seconds = 60
    seconds_wait = 5

    for n_try in range(max_seconds // seconds_wait):
        if not util.ping():
            error('Connection not found')
            time.sleep(seconds_wait)
        elif n_try:
            log('Connection found')
            break
        else:
            break
    else:  # no break; really no internet connection
        error('Too many tries')
        return 1

    save_dir = pathlib.Path(save_dir)
    save_dir.mkdir(exist_ok=True)

    urls = (
        post['data']['url']
        for post in get(url).json()['data']['children'])

    with download.saving():
        for res in random_map(download, urls):
            if not res.succeeded:
                error(res.status, res.url, sep=': ')
                continue
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

"""Global package settings"""
import pathlib

CACHE_PATH = str(pathlib.Path.home() / '.cache/wal/collect.pickle')
REDDIT_LINK = 'https://www.reddit.com/r/earthporn/hot/.json?limit=10'
SAVE_DIR = '/tmp/wal'

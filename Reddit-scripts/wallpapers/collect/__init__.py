"""Automate downloading a picture from reddit.

Prints verbose log info to stderr and downloaded image path to stdout for easy
redirection."""
from .config import CACHE_PATH, REDDIT_LINK, SAVE_DIR
from . import util, cache, collect
from .__main__ import main

if 'confuse anaconda':
    CACHE_PATH, REDDIT_LINK, SAVE_DIR, util, cache, collect, main

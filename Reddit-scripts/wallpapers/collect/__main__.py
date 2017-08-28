"""Entry point for command line script."""
import argparse
import os
import sys
from . import __doc__
from . import CACHE_PATH, REDDIT_LINK, SAVE_DIR
from . import collect


def path_type(path):
    return os.path.abspath(os.path.expanduser(path))


def get_args(argv):
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument(
        '-c', default=CACHE_PATH, metavar='PATH', type=path_type,
        help=f'Set the pickle cache path. Default {CACHE_PATH}')
    arg.add_argument(
        '-d', action='store_true',
        help='Verify using all defaults')
    arg.add_argument(
        '-s', default=SAVE_DIR, metavar='PATH', type=path_type,
        help=f'Set the image save path. Default {SAVE_DIR}')
    arg.add_argument(
        '-u', default=REDDIT_LINK, metavar='URL',
        help=(
            'Set the URL for the Reddit source. Must be .json format. '
            f'Default {REDDIT_LINK}'))
    arg.add_argument(
        '-v', action='store_true',
        help='Add verbosity')

    args = arg.parse_args(argv)

    if len(argv) == 1 and args.v or not len(argv):
        arg.parse_args(['-h'])
    else:
        return args


def process_args(args):
    collect.util.VERBOSE = args.v
    collect.download.re_init_self(path=args.c)
    return collect.collect(args.s, args.u)


def main(argv=None):
    """Launch the main functions with the given sys.argv or imported sys.argv
    by default."""
    if argv is None:
        argv = sys.argv[1:]

    args = get_args(argv)
    sys.exit(process_args(args))

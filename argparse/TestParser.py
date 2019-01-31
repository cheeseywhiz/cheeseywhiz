"""Test Parser"""
import argparse


class TestParser(argparse.ArgumentParser):
    def __init__(self, *args, description=__doc__, **kwargs):
        super().__init__(*args, description=description, **kwargs)


test_parser = TestParser(add_help=True)

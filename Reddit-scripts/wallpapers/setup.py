"""python setup.py install"""
import setuptools

setuptools.setup(
    name='collect',
    version='1.0',
    packages=['collect'],
    entry_points={
        "console_scripts": ["collect=collect.__main__:main"]
    },)

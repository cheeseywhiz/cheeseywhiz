from setuptools import setup, Extension

mdbsmodule = Extension(
    'mdbs',
    sources=['mdbsmodule.c'])

setup(
    ext_modules=[mdbsmodule])

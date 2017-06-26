#!/usr/bin/env python3
"""
Take the average of each pixel for each picture in the source directory. Each
image must be exactly the same size.

avgimg.py [arguments] [source directory]

[source directory]:
    Directory to pull images from.

[arguments]:
    [-avg]=[mean, median, min, max]:
        Change averaging operation. Default is mean.
    [-c]=[color map]:
        Give the output image a new color set. See -hc for options.
    [-h]:
        Print this help message and quit.
    [-hc]:
        Print color map options and quit.
    [-i]:
        Toggle default invert colors option. Default is %s.
    [-o]=[output filename]:
        Filename of new output image. Default output.png in current working
        directory.
    [+o]:
        The output saved temporarily in /tmp. Intended to be used with -s.
    [-s]=[feh, mpl]:
        Open the image on exit.
            feh: Open with feh
            mpl: Open with matplotlib
    [-v]:
        Print out parsed arguments.
"""
from os import listdir, path
from sys import exit, argv

from numpy import empty
from matplotlib import pyplot as plt

from imglib import colormaps, ImageIter, load_global, trim


class Container:
    @property
    def CMAP(self):
        if self.GRAYSCALE:
            return self.cmap
        else:
            return None

    @CMAP.setter
    def CMAP(self, cmap):
        try:
            self.cmap = plt.get_cmap(cmap)
        except ValueError:
            print(f'Unknown color map {cmap}. Options:\n{colormaps()}')


g = Container()
load_global(g)

g.INVERT = True
g.GRAYSCALE = False
g.CMAP = 'Accent'
__doc__ = __doc__[1:-1]%g.INVERT
g.__DOC__ = __doc__


def zip_iterables(*iterables):
    generators = [iter(iterable) for iterable in iterables]
    while True:
        try:
            yield [next(generator) for generator in generators]
        except StopIteration:
            break


def make_image(argv):
    imgs_dir, avg_func, fname, exit_func = trim(argv)
    img_px = []

    for image_ in listdir(imgs_dir):
        image = path.join(imgs_dir, image_)
        img_px.append(ImageIter(image))

    width = img_px[0].width
    height = img_px[0].height
    color_len = img_px[0].color_len

    new_img = empty(
        (width, height, color_len)[:(2 if g.GRAYSCALE else 3)]
    )

    for pixel_info_list in zip_iterables(*img_px):
        px_list, py_list, colors = zip(*pixel_info_list)
        px, py = px_list[0], py_list[0]
        new_img[px][py] = avg_func(colors)

    plt.imsave(fname, new_img, cmap=g.CMAP)
    exit_func(array=new_img, fname=fname)


def main(argv):
    try:
        make_image(argv)
    except KeyboardInterrupt:
        exit('\nStopped by user')


if __name__ == '__main__':
    main(argv)

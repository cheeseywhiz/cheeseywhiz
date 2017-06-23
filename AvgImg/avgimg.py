#!/usr/bin/env python3
"""
Take the average of each pixel for each picture in the source directory. Each
image must be exactly the same size.

avgimg.py [arguments]

[arguments]
Required:
    [source directory]:
        Directory to pull images from.

Optional:
    [-avg [mean, median, min, max]]:
        Change averaging operation. Default is mean.
    [-g]:
        Turn the output image into grayscale.
    [-h]:
        Print this help message and quit.
    [-i]:
        Toggle default invert colors option. Default is %s.
    [-o [output filename]]:
        Filename of new output image. Default output.png in current working
        directory.
    [+o]:
        The output saved temporarily in /tmp. Intended to be used with -s.
    [-s [feh, mpl]]:
        Open the image on exit.
            feh: Open with feh
            mpl: Open with matplotlib
    [-v]:
        Print out parsed arguments.
"""
import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from avgimglib.mplimageiter import ImageIter
from avgimglib import trim, load_global


class container:
    @property
    def CMAP(self):
        return plt.get_cmap('Greys') if self.GRAYSCALE else None

    @CMAP.setter
    def CMAP(self, cmap):
        return plt.get_cmap(cmap) if self.GRAYSCALE else None


g = container()
load_global(g)

g.INVERT = True
g.GRAYSCALE = False
__doc__ = __doc__[1:-1]%g.INVERT
g.__DOC__ = __doc__


def zip_iterables(*iterables):
    generators = [iter(iterable) for iterable in iterables]
    while True:
        try:
            yield [next(generator) for generator in generators]
        except StopIteration:
            break


def main(argv):
    imgs_dir, avg_func, fname, exit_func = trim(argv)
    img_px = []

    for image_ in os.listdir(imgs_dir):
        image = os.path.join(imgs_dir, image_)
        img_px.append(ImageIter(image))

    width = img_px[0].width
    height = img_px[0].height
    color_len = img_px[0].color_len

    new_img = np.empty((width, height, color_len))

    for pixel_info_list in zip_iterables(*img_px):
        px_list, py_list, colors = zip(*pixel_info_list)
        px, py = px_list[0], py_list[0]
        new_img[px][py] = avg_func(colors)

    plt.imsave(fname, new_img, cmap=g.CMAP)
    exit_func(array=new_img, fname=fname)


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        sys.exit('\nStopped by user')

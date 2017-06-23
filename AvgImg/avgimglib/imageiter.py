from PIL import Image


class ImageIter:
    def __init__(self, fname=None, inst=None):
        """
        Create a PIL PyAccess.PyAccess-like object that has a few improvements.

        Create from an image on file (fname) or from a PIL.Image.Image
        instance (inst).
        """
        if fname is not None:
            self.inst = Image.open(fname).__copy__()
        else:
            self.inst = inst

        self._px_map = self.inst.load()

    def __getitem__(self, xy: tuple):
        """
        self[x, y]

        Return RGB color tuple at position (x, y).
        """
        return self._px_map[xy]

    def __iter__(self):
        """
        Return a generator that yields a 3-tuple of the x coordinate, y
        coordinate, and color tuple for each pixel in the image.
        """
        def yield_coords(skeleton):
            # set up loop to make indices generator
            def recur(obj, *index):
                if hasattr(obj, '__iter__'):
                    return (
                        recur(item, *index, i)
                        for i, item in enumerate(obj)
                    )
                else:
                    return index

            # flatten the recur generator
            for row in recur(skeleton):
                for px in row:
                    yield px

        coords = yield_coords(
            (None
             for i in range(self.inst.height))
            for j in range(self.inst.width)
        )

        return (
            (x, y, self.__getitem__((x, y)))
            for x, y in coords
        )

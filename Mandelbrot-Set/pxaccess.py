class PixelAccess_Int:
    """
    An interface for more easily interacting with PixelAccess objects from PIL.
    """

    def px_field(self):
        """
        Yield a 3-tuple of the pixel index tuple, the graph x value, and the
        graph y value for each pixel in the image.
        """
        for px, py in self.px_map.keys():
            x = px * (self.xmax - self.xmin) / self.width + self.xmin
            y = py * (self.ymin - self.ymax) / self.height + self.ymax
            yield (px, py), x, y

    def map(self, f):
        """
        Pass the graph x and y value to the specified function and set the
        corresponding pixel to the result.
        """
        for i, x, y in self.px_field():
            self.px_map[i] = f(x, y)

    def save(self, fname, mode, color=0):
        """
        Save the image in its current state under file name fname.

        mode and color=0 are sent to PIL.Image.new.
        """
        from PIL import Image
        new = Image.new(mode, (self.width, self.height), color)
        pixel = new.load()
        for px in self.px_map:
            pixel[px] = self.px_map[px]
        new.convert('RGB').save(fname)

    def _R(self, obj):
        """
        Create an R-like subscriptable object from a multidimensional list.
        """
        res = {}

        def recur(obj, *index):
            try:
                iter(obj)
            except TypeError:
                res[tuple(index)] = obj
            else:
                for i, item in enumerate(obj):
                    recur(item, *index, i)

        recur(obj)
        return res

    def __init__(self, xmin, xmax, ymin, ymax, width, height):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.width = width
        self.height = height
        self.px_map = self._R(
            [0
             for i in range(self.width)]
            for j in range(self.height))

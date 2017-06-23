from matplotlib import pyplot as _plt


class ImageIter:
    def __init__(self, fname=None, px_map=None):
        if fname is not None:
            self.px_map = _plt.imread(fname)
        elif px_map is not None:
            self.px_map = px_map

        self.width, self.height, self.color_len = self.px_map.shape

    def __getitem__(self, row):
        return self.px_map[row]

    def __iter__(self):
        return (
            (row, col, self.__getitem__(row)[col])
            for row in range(self.width)
            for col in range(self.height)
        )

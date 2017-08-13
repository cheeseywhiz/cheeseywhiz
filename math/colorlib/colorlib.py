import numpy as np


def vector(func):
    def decorated_func(*args, **kwargs):
        return (np.vectorize(func))(*args, **kwargs)

    return decorated_func


def closest_rgb(input_color, pallette):
    np_pallette = np.array(pallette)
    np_input_color = np.array(input_color)

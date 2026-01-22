from skimage import io
import numpy as np
from pyxelate import Pyx, Pal  # https://github.com/sedthh/pyxelate/tree/master

try:
    from legoify import indicator
except ImportError:
    import indicator

try:
    from legoify import util
except ImportError:
    import util

SCALE = 12

def pixelate(image_path, height, width=None, dither=None):
    width = height if width is None else width
    lego_pal = Pal.from_rgb(util.get_lego_colors(True))
    in_image = io.imread(image_path)
    pyx = Pyx(height=height, width=width, palette=lego_pal, dither=dither)
    pyx.fit(in_image)
    out_image = pyx.transform(in_image)
    return out_image


def get_color_filter(pyx_image, color):
    mask = (
        (pyx_image[:, :, 0] == color[0])
        & (pyx_image[:, :, 1] == color[1])
        & (pyx_image[:, :, 2] == color[2])
    )
    mask = np.reshape(np.repeat(mask, 3), np.shape(pyx_image))
    bg_color = 0 if util.black_or_white(color) == [0, 0, 0] else 255
    return np.where(mask, pyx_image, bg_color)


def get_zoomed_image(pyx_image, scale=12):
    rows_zoomed = np.repeat(pyx_image, scale, axis=0)
    zoomed = np.repeat(rows_zoomed, scale, axis=1)
    return zoomed


def draw_block_indicator(zoomed_image):
    fit_shape = (zoomed_image.shape[0] // SCALE, zoomed_image.shape[1] // SCALE, 1)
    indicator_fitted = np.tile(indicator.indicator, fit_shape)
    return util.mix_array(zoomed_image, indicator_fitted).astype(np.uint8)
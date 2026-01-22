import numpy as np
from pathlib import Path


def get_lego_colors(colors_only=False):
    colors = []
    gpl_path = Path(__file__).parent / "LEGO.GPL"
    with open(gpl_path, "r") as f:
        lines = f.readlines()
    for line in lines[4:]:
        r = int(line[0:3].strip())
        g = int(line[4:7].strip())
        b = int(line[8:11].strip())
        if colors_only:
            colors.append((r, g, b))
            continue
        name = line[19:].strip()
        partno = line[12:19].strip()
        colors.append([(r, g, b), name, partno])
    return colors


def color_name_to_rgb(name):
    colors = get_lego_colors(False)
    for color in colors:
        if color[1] == name:
            return color[0]


def black_or_white(color):
    r, g, b = color

    # 1. Convert sRGB to linear RGB space
    # The W3C formula requires this linearization step
    def linearize_color(c):
        c /= 255.0
        if c <= 0.04045:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    r_lin = linearize_color(r)
    g_lin = linearize_color(g)
    b_lin = linearize_color(b)

    # 2. Calculate the relative luminance (L) using the ITU-R BT.709 formula
    # Human eyes favor green, so it has a higher weight
    L = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    # 3. Determine the best text color based on luminance
    # A simplified threshold derived from the W3C contrast formula is L > 0.179.
    # If L is greater than the threshold, the background is considered "light"
    # and black text is preferred. Otherwise, white text is better.
    if L > 0.179:
        return [0, 0, 0]  # Use black text
    else:
        return [255, 255, 255]  # Use white text


def mix(base, overlay, alpha):
    base_d = base / 255.0
    overlay_d = overlay / 255.0
    alpha_d = alpha / 255.0
    distance = overlay_d - base_d
    return (base_d + alpha_d * distance) * 255


def mix_array(base_array, overlay_array):
    # Add alpha
    if np.shape(base_array)[2] < 4:
        base_alpha = (
            np.ones(base_array.shape[:2], dtype=base_array.dtype) * 255
        )  # For uint8
        base_array = np.dstack((base_array, base_alpha))
    base_rgb = base_array[..., :-1]
    overlay_rgb = overlay_array[..., :-1]
    alpha = overlay_array[..., -1].repeat(3).reshape(base_array.shape[:2] + (3,))

    return mix(base_rgb, overlay_rgb, alpha)

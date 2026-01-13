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

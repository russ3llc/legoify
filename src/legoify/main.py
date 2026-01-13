# python 3.9.2
import csv
import argparse
import numpy as np
from pathlib import Path
from skimage import io
from pyxelate import Pyx, Pal  # https://github.com/sedthh/pyxelate/tree/master

try:
    from . import util
except ImportError:
    try:
        from legoify import util
    except ImportError:
        import util

parser = argparse.ArgumentParser(
    description="A program to create a mosiac from an image using LEGO colors, and output the part list."
)
parser.add_argument("input_path", type=str, help="The path to the input image")
parser.add_argument("height", type=int, help="The height of the output image")
parser.add_argument(
    "-o",
    "--output_dir",
    type=str,
    help="The path to output images. Defaults to 'Output'",
    default="Output\\",
)
parser.add_argument(
    "-w",
    "--width",
    type=int,
    default=None,
    help="The width of the output image. Defaults to height if not specified",
)
parser.add_argument(
    "-d",
    "--dither",
    type=str,
    default=None,
    help="The dither algorithm to use - None (default), 'naive', 'bayer', 'floyd', 'atkinson' (ordered fastest to slowest)",
    choices=[None, "naive", "bayer", "floyd", "atkinson"],
)
parser.add_argument(
    "-c",
    "--color_filters",
    action="store_true",
    help="Save additional reference images of individual colors",
)


# Dither = "none", "naive", "bayer", "floyd", "atkinson" (fastest to slowest)
def pixelate(image_path, height, width=None, dither=None):
    width = height if width is None else width
    lego_pal = Pal.from_rgb(util.get_lego_colors(True))
    in_image = io.imread(image_path)
    pyx = Pyx(height=height, width=width, palette=lego_pal, dither=dither)
    pyx.fit(in_image)
    out_image = pyx.transform(in_image)
    return out_image


def get_color_filter(in_image, color):
    mask = (
        (in_image[:, :, 0] == color[0])
        & (in_image[:, :, 1] == color[1])
        & (in_image[:, :, 2] == color[2])
    )
    mask = np.reshape(np.repeat(mask, 3), np.shape(in_image))
    bg_color = 0 if util.black_or_white(color) == [0, 0, 0] else 255
    return np.where(mask, in_image, bg_color)


def get_zoomed_image(in_image, scale=12):
    rows_zoomed = np.repeat(in_image, scale, axis=0)
    zoomed = np.repeat(rows_zoomed, scale, axis=1)
    return zoomed


def draw_pixel_indicators(in_image, scale=12):
    # border
    in_image[0:, 0::scale] = [0, 0, 0]
    in_image[0:, scale - 1 :: scale] = [0, 0, 0]
    in_image[0::scale, 0:] = [0, 0, 0]
    in_image[scale - 1 :: scale, 0:] = [0, 0, 0]
    # center
    in_image[5::scale, 5::scale] = [255, 255, 255]
    in_image[6::scale, 5::scale] = [255, 255, 255]
    in_image[5::scale, 6::scale] = [255, 255, 255]
    in_image[6::scale, 6::scale] = [255, 255, 255]
    return in_image


def get_part_list(out_im):
    lego_colors = util.get_lego_colors()
    image_colors = out_im.reshape(-1, 3)
    part_list = [
        dict(
            colorName=lc[1],
            elementId=lc[2],
            quantity=len(
                [
                    c
                    for c in image_colors
                    if c[0] == lc[0][0] and c[1] == lc[0][1] and c[2] == lc[0][2]
                ]
            ),
        )
        for lc in lego_colors
    ]
    # Remove colors with 0 count
    return [p for p in part_list if p["quantity"] > 0]


def main():
    args = parser.parse_args()
    args.width = args.height if args.width is None else args.width
    pyx_image = pixelate(Path(args.input_path), args.height, args.width, args.dither)
    # io.imsave(args.output_dir + "to_scale.png", pyx_image)

    out_path = Path(args.output_dir)
    Path.mkdir(out_path, parents=True, exist_ok=True)
    zoomed = get_zoomed_image(pyx_image)
    bordered = draw_pixel_indicators(zoomed)
    io.imsave(Path(out_path, "output.png"), bordered)

    part_list = get_part_list(pyx_image)
    csv_out_path = Path(args.output_dir)
    Path.mkdir(csv_out_path, parents=True, exist_ok=True)
    with open(Path(csv_out_path, "part_list.csv"), "w") as f:
        writer = csv.DictWriter(f, fieldnames=["elementId", "quantity", "colorName"])
        # writer = csv.DictWriter(f, fieldnames=["part_no", "count", "color_name"])
        writer.writeheader()
        writer.writerows(part_list)

    if args.color_filters:
        used_colors_names = [p["colorName"] for p in part_list]
        colors_path = Path(args.output_dir, "colors")
        Path.mkdir(colors_path, parents=True, exist_ok=True)
        for color_name in used_colors_names:
            color = util.color_name_to_rgb(color_name)
            color_filter = get_color_filter(pyx_image, color)
            zoomed_color_filter = get_zoomed_image(color_filter)
            bordered_color_filter = draw_pixel_indicators(zoomed_color_filter)
            io.imsave(
                Path(colors_path, color_name + ".png"),
                bordered_color_filter,
            )

    print("Done!")


if __name__ == "__main__":
    main()
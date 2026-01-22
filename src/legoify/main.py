import csv
import argparse
import warnings
from pathlib import Path
from skimage import io

try:
    from legoify import image
except ImportError:
    import image

try:
    from legoify import parts
except ImportError:
    import parts

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

def write_part_list(part_list, output_dir):
    if parts.should_split_part_list(part_list):
        warnings.warn(
            "Part list contains more than 999 of the same color. Splitting into multiple part lists."
        )
        part_lists = parts.split_part_list(part_list)
    else:
        part_lists = [part_list]
    csv_out_path = Path(output_dir)
    Path.mkdir(csv_out_path, parents=True, exist_ok=True)
    for i, pl in enumerate(part_lists):
        file_name = "part_list.csv" if i == 0 else f"part_list_{i}.csv"
        with open(Path(csv_out_path, file_name), "w") as f:
            writer = csv.DictWriter(
                f, fieldnames=["elementId", "quantity", "colorName"]
            )
            writer.writeheader()
            writer.writerows(pl)

def write_color_filters(part_list, pyx_image, output_dir):
    used_colors_names = [p["colorName"] for p in part_list]
    colors_path = Path(output_dir, "colors")
    Path.mkdir(colors_path, parents=True, exist_ok=True)
    for color_name in used_colors_names:
        color = util.color_name_to_rgb(color_name)
        color_filter = image.get_color_filter(pyx_image, color)
        zoomed_color_filter = image.get_zoomed_image(color_filter)
        bordered_color_filter = image.draw_block_indicator(zoomed_color_filter)
        io.imsave(
            Path(colors_path, color_name + ".png"),
            bordered_color_filter,
        )

def main():
    args = parser.parse_args()
    args.width = args.height if args.width is None else args.width

    out_path = Path(args.output_dir)
    Path.mkdir(out_path, parents=True, exist_ok=True)

    pyx_image = image.pixelate(Path(args.input_path), args.height, args.width, args.dither)
    io.imsave(Path(out_path, "pyx.png"), pyx_image)
    zoomed = image.get_zoomed_image(pyx_image)
    bordered = image.draw_block_indicator(zoomed)
    io.imsave(Path(out_path, "output.png"), bordered)

    part_list = parts.get_part_list(pyx_image)
    write_part_list(part_list, args.output_dir)

    if args.color_filters:
        write_color_filters(part_list, pyx_image, args.output_dir)

    print("Done!")


if __name__ == "__main__":
    main()

from collections import defaultdict

try:
    from legoify import util
except ImportError:
    import util

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


def should_split_part_list(part_list):
    quantities = [p["quantity"] for p in part_list]
    return max(quantities) > 999


def split_part_list(part_list, max_quantity=999):
    chunks_by_color = defaultdict(list)

    for part in part_list:
        remaining = part["quantity"]
        while remaining > 0:
            chunk = min(max_quantity, remaining)
            remaining -= chunk
            chunks_by_color[part["colorName"]].append(
                {
                    "colorName": part["colorName"],
                    "elementId": part["elementId"],
                    "quantity": chunk,
                }
            )

    num_lists = max(len(chunks) for chunks in chunks_by_color.values())

    result_lists = [[] for _ in range(num_lists)]

    for part in part_list:
        color = part["colorName"]
        chunks = chunks_by_color[color]

        for i, chunk in enumerate(chunks):
            result_lists[i].append(chunk)

        chunks_by_color[color] = []

    return result_lists
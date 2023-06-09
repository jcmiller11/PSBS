from textwrap import wrap

from PIL import Image


def rgba_to_hex(rgba_tuple, alpha=False):
    output = ""
    if rgba_tuple[3] == 0:
        return "transparent"
    if not alpha:
        rgba_tuple = rgba_tuple[:-1]
    for value in rgba_tuple:
        output += format(value, "x").zfill(2)
    return f"#{output}"


def pixel_list_to_sprite(pixel_values, width=5, alpha=False):
    colors = {}
    colors["transparent"] = None
    for pixel in pixel_values:
        colors[rgba_to_hex(pixel, alpha)] = None

    colors_list = list(colors.keys())

    sprite = ""

    for pixel in pixel_values:
        color = colors_list.index(rgba_to_hex(pixel, alpha)) - 1
        if color == -1:
            color = "."
        sprite += str(color)

    sprite = wrap(sprite, width)
    sprite = "\n".join(sprite)
    return {"sprite": sprite, "colors": colors}


def image_to_object(file, name="", alpha=False):
    image = Image.open(file, "r")
    image = image.convert("RGBA")
    result = pixel_list_to_sprite(
        image.getdata(), width=image.size[0], alpha=alpha
    )
    sprite = result["sprite"]
    colors = result["colors"]
    if len(colors) > 10:
        if "." in sprite:
            image = image.quantize(colors=11)
        else:
            image = image.quantize(colors=10)
        image = image.convert("RGBA")
        result = pixel_list_to_sprite(
            image.getdata(), width=image.size[0], alpha=alpha
        )
        sprite = result["sprite"]
        colors = result["colors"]
    colors.pop("transparent", None)
    return f'{name}\n{" ".join(colors)}\n{sprite}'.strip()

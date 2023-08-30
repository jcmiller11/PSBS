from textwrap import wrap

from PIL import Image
from psbs.extension import Extension


class Images(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register("image", self.image_to_object)
        self.loaded_images = {}

    @staticmethod
    def get_config():
        return {"alpha": False, "max_colors": 10}

    def __rgba_to_hex(self, rgba_tuple):
        if rgba_tuple[3] == 0:
            return "transparent"
        if not self.config["alpha"]:
            rgba_tuple = rgba_tuple[:-1]
        return "#" + "".join([format(value, "02x") for value in rgba_tuple])

    def __pixel_list_to_sprite(self, pixel_values, width):
        colors = {"transparent": None}
        colors.update(
            {self.__rgba_to_hex(pixel): None for pixel in pixel_values}
        )
        colors = list(colors)

        sprite = []
        for pixel in pixel_values:
            color = colors.index(self.__rgba_to_hex(pixel)) - 1
            if color == -1:
                sprite.append(".")
            else:
                sprite.append(
                    str(color) if color < 10 else chr(ord("a") + color - 10)
                )

        return {
            "sprite": "\n".join(wrap("".join(sprite), width)),
            "colors": colors,
        }

    def image_to_object(
        self,
        file,
        left=0,
        top=0,
        width=None,
        height=None,
    ):
        # Warn if max_colors too high
        if self.config["max_colors"] > 36:
            print("Warning: max_colors config values over 36 not supported")
            self.config["max_colors"] = 36

        if file in self.loaded_images:
            image = self.loaded_images[file]
        else:
            try:
                image = Image.open(file, "r")
            except IOError as err:
                raise self.ExtensionError(
                    f"Unable to read image file\n  {err}"
                )
            self.loaded_images[file] = image

        # Crop image if needed
        right = left + width if width else image.size[0]
        bottom = top + height if height else image.size[1]
        image = image.crop((left, top, right, bottom)).convert("RGBA")

        # Generate sprite
        result = self.__pixel_list_to_sprite(
            image.getdata(), width=image.size[0]
        )
        sprite, colors = result["sprite"], result["colors"]

        # Reduce number of colors if more max
        max_colors = self.config["max_colors"]
        if "." in sprite:
            max_colors += 1
        if len(colors) > max_colors:
            # Warn if quantizing
            print(f"Warning: image {file} has too many colors")
            print("  Attempting to quantize")
            image = image.quantize(colors=max_colors)
            image = image.convert("RGBA")
            result = self.__pixel_list_to_sprite(
                image.getdata(), width=image.size[0]
            )
            sprite, colors = result["sprite"], result["colors"]

        # Remove transparent unless it's the only color
        if len(colors) > 1 and "transparent" in colors:
            colors.remove("transparent")

        return f'{" ".join(colors)}\n{sprite}'

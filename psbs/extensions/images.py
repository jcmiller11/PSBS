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
        output = ""
        if rgba_tuple[3] == 0:
            return "transparent"
        if not self.config["alpha"]:
            rgba_tuple = rgba_tuple[:-1]
        for value in rgba_tuple:
            output += format(value, "x").zfill(2)
        return f"#{output}"

    def __pixel_list_to_sprite(self, pixel_values, width):
        colors = {}
        colors["transparent"] = None
        for pixel in pixel_values:
            colors[self.__rgba_to_hex(pixel)] = None

        colors_list = list(colors.keys())

        sprite = ""

        for pixel in pixel_values:
            color = colors_list.index(self.__rgba_to_hex(pixel)) - 1
            if color > 9:
                color = chr(ord("a") + color - 10)
            if color == -1:
                color = "."
            sprite += str(color)

        sprite = wrap(sprite, width)
        sprite = "\n".join(sprite)
        return {"sprite": sprite, "colors": colors}

    def image_to_object(
        self,
        file,
        left=0,
        top=0,
        width=None,
        height=None,
    ):
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
        if width:
            right = left + width
        else:
            right = image.size[0]
        if height:
            bottom = top + height
        else:
            bottom = image.size[1]
        image = image.crop((left, top, right, bottom))
        image = image.convert("RGBA")
        result = self.__pixel_list_to_sprite(
            image.getdata(), width=image.size[0]
        )
        sprite = result["sprite"]
        colors = result["colors"]
        if len(colors) > 10:
            if "." in sprite:
                image = image.quantize(colors=self.config["max_colors"] + 1)
            else:
                image = image.quantize(colors=self.config["max_colors"])
            image = image.convert("RGBA")
            result = self.__pixel_list_to_sprite(
                image.getdata(), width=image.size[0]
            )
            sprite = result["sprite"]
            colors = result["colors"]
        if len(colors) > 1:
            colors.pop("transparent", None)
        return f'{" ".join(colors)}\n{sprite}'

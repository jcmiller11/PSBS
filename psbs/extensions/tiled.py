from os import path
import shutil
from xml.etree import ElementTree
from xml.dom import minidom
from PIL import Image, ImageColor
from numpy import array, uint8
from psbs.errors import PSBSError
from psbs.extension import Extension
from psbs.psparser import PSParser
from psbs.utils import make_dir, write_file


class Tiled(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register("tiled", self.parse_level)
        self.register_post(self.write_tileset_files)

    @staticmethod
    def get_config():
        return {"generate_tileset": False}

    def __object_to_pixels(
        self, object_string, size=5, palette_name="arnecolors"
    ):
        if "\n" not in object_string:
            colors_string = object_string
            pixels_string = "\n".join(["0" * size] * size)
        else:
            colors_string, pixels_string = object_string.split("\n", 1)
        colors = [ImageColor.getcolor("#00000000", "RGBA")]
        for color in colors_string.split():
            colors.append(
                self.__color_to_rgba(color, palette_name=palette_name)
            )
        image_list = []
        for line in pixels_string.split("\n"):
            line_list = []
            for char in line:
                # Handle alpha values for colors > 10
                if char.isalpha():
                    char = ord(char.lower()) - ord("a") + 10
                # Handle transparency
                elif char == ".":
                    char = -1
                else:
                    char = int(char)
                line_list.append(colors[char + 1])
            image_list.append(line_list)
        return Image.fromarray(array(image_list, dtype=uint8), mode="RGBA")

    def __color_to_rgba(self, color, palette_name="arnecolors"):
        color_palettes = {
            "mastersystem": {
                "black": "#000000",
                "white": "#FFFFFF",
                "grey": "#555555",
                "darkgrey": "#555500",
                "lightgrey": "#AAAAAA",
                "gray": "#555555",
                "darkgray": "#555500",
                "lightgray": "#AAAAAA",
                "red": "#FF0000",
                "darkred": "#AA0000",
                "lightred": "#FF5555",
                "brown": "#AA5500",
                "darkbrown": "#550000",
                "lightbrown": "#FFAA00",
                "orange": "#FF5500",
                "yellow": "#FFFF55",
                "green": "#55AA00",
                "darkgreen": "#005500",
                "lightgreen": "#AAFF00",
                "blue": "#5555AA",
                "lightblue": "#AAFFFF",
                "darkblue": "#000055",
                "purple": "#550055",
                "pink": "#FFAAFF",
            },
            "gameboycolour": {
                "black": "#000000",
                "white": "#FFFFFF",
                "grey": "#7F7F7C",
                "darkgrey": "#3E3E44",
                "lightgrey": "#BAA7A7",
                "gray": "#7F7F7C",
                "darkgray": "#3E3E44",
                "lightgray": "#BAA7A7",
                "red": "#A7120C",
                "darkred": "#880606",
                "lightred": "#BA381F",
                "brown": "#57381F",
                "darkbrown": "#3E2519",
                "lightbrown": "#8E634B",
                "orange": "#BA4B32",
                "yellow": "#C0BA6F",
                "green": "#517525",
                "darkgreen": "#385D12",
                "lightgreen": "#6F8E44",
                "blue": "#5D6FA7",
                "lightblue": "#8EA7A7",
                "darkblue": "#4B575D",
                "purple": "#3E3E44",
                "pink": "#BA381F",
            },
            "amiga": {
                "black": "#000000",
                "white": "#FFFFFF",
                "grey": "#BBBBBB",
                "darkgrey": "#333333",
                "lightgrey": "#FFEEDD",
                "gray": "#BBBBBB",
                "darkgray": "#333333",
                "lightgray": "#FFEEDD",
                "red": "#DD1111",
                "darkred": "#990000",
                "lightred": "#FF4422",
                "brown": "#663311",
                "darkbrown": "#331100",
                "lightbrown": "#AA6644",
                "orange": "#FF6644",
                "yellow": "#FFDD66",
                "green": "#448811",
                "darkgreen": "#335500",
                "lightgreen": "#88BB77",
                "blue": "#8899DD",
                "lightblue": "#BBDDEE",
                "darkblue": "#666688",
                "purple": "#665555",
                "pink": "#997788",
            },
            "arnecolors": {
                "black": "#000000",
                "white": "#FFFFFF",
                "grey": "#9d9d9d",
                "darkgrey": "#697175",
                "lightgrey": "#cccccc",
                "gray": "#9d9d9d",
                "darkgray": "#697175",
                "lightgray": "#cccccc",
                "red": "#be2633",
                "darkred": "#732930",
                "lightred": "#e06f8b",
                "brown": "#a46422",
                "darkbrown": "#493c2b",
                "lightbrown": "#eeb62f",
                "orange": "#eb8931",
                "yellow": "#f7e26b",
                "green": "#44891a",
                "darkgreen": "#2f484e",
                "lightgreen": "#a3ce27",
                "blue": "#1d57f7",
                "lightblue": "#B2DCEF",
                "darkblue": "#1B2632",
                "purple": "#342a97",
                "pink": "#de65e2",
            },
            "famicom": {
                "black": "#000000",
                "white": "#ffffff",
                "grey": "#7c7c7c",
                "darkgrey": "#080808",
                "lightgrey": "#bcbcbc",
                "gray": "#7c7c7c",
                "darkgray": "#080808",
                "lightgray": "#bcbcbc",
                "red": "#f83800",
                "darkred": "#881400",
                "lightred": "#f87858",
                "brown": "#AC7C00",
                "darkbrown": "#503000",
                "lightbrown": "#FCE0A8",
                "orange": "#FCA044",
                "yellow": "#F8B800",
                "green": "#00B800",
                "darkgreen": "#005800",
                "lightgreen": "#B8F8B8",
                "blue": "#0058F8",
                "lightblue": "#3CBCFC",
                "darkblue": "#0000BC",
                "purple": "#6644FC",
                "pink": "#F878F8",
            },
            "atari": {
                "black": "#000000",
                "white": "#FFFFFF",
                "grey": "#909090",
                "darkgrey": "#404040",
                "lightgrey": "#b0b0b0",
                "gray": "#909090",
                "darkgray": "#404040",
                "lightgray": "#b0b0b0",
                "red": "#A03C50",
                "darkred": "#700014",
                "lightred": "#DC849C",
                "brown": "#805020",
                "darkbrown": "#703400",
                "lightbrown": "#CB9870",
                "orange": "#CCAC70",
                "yellow": "#ECD09C",
                "green": "#58B06C",
                "darkgreen": "#006414",
                "lightgreen": "#70C484",
                "blue": "#1C3C88",
                "lightblue": "#6888C8",
                "darkblue": "#000088",
                "purple": "#3C0080",
                "pink": "#B484DC",
            },
            "pastel": {
                "black": "#000000",
                "white": "#FFFFFF",
                "grey": "#3e3e3e",
                "darkgrey": "#313131",
                "lightgrey": "#9cbcbc",
                "gray": "#3e3e3e",
                "darkgray": "#313131",
                "lightgray": "#9cbcbc",
                "red": "#f56ca2",
                "darkred": "#a63577",
                "lightred": "#ffa9cf",
                "brown": "#b58c53",
                "darkbrown": "#787562",
                "lightbrown": "#B58C53",
                "orange": "#EB792D",
                "yellow": "#FFe15F",
                "green": "#00FF4F",
                "darkgreen": "#2b732c",
                "lightgreen": "#97c04f",
                "blue": "#0f88d3",
                "lightblue": "#00fffe",
                "darkblue": "#293a7b",
                "purple": "#ff6554",
                "pink": "#eb792d",
            },
            "ega": {
                "black": "#000000",
                "white": "#ffffff",
                "grey": "#555555",
                "darkgrey": "#555555",
                "lightgrey": "#aaaaaa",
                "gray": "#555555",
                "darkgray": "#555555",
                "lightgray": "#aaaaaa",
                "red": "#ff5555",
                "darkred": "#aa0000",
                "lightred": "#ff55ff",
                "brown": "#aa5500",
                "darkbrown": "#aa5500",
                "lightbrown": "#ffff55",
                "orange": "#ff5555",
                "yellow": "#ffff55",
                "green": "#00aa00",
                "darkgreen": "#00aaaa",
                "lightgreen": "#55ff55",
                "blue": "#5555ff",
                "lightblue": "#55ffff",
                "darkblue": "#0000aa",
                "purple": "#aa00aa",
                "pink": "#ff55ff",
            },
            "proteus_mellow": {
                "black": "#3d2d2e",
                "white": "#ddf1fc",
                "grey": "#9fb2d4",
                "darkgrey": "#7b8272",
                "lightgrey": "#a4bfda",
                "gray": "#9fb2d4",
                "darkgray": "#7b8272",
                "lightgray": "#a4bfda",
                "red": "#9d5443",
                "darkred": "#8c5b4a",
                "lightred": "#94614c",
                "brown": "#89a78d",
                "darkbrown": "#829e88",
                "lightbrown": "#aaae97",
                "orange": "#d1ba86",
                "yellow": "#d6cda2",
                "green": "#75ac8d",
                "darkgreen": "#8fa67f",
                "lightgreen": "#8eb682",
                "blue": "#88a3ce",
                "lightblue": "#a5adb0",
                "darkblue": "#5c6b8c",
                "purple": "#d39fac",
                "pink": "#c8ac9e",
            },
            "proteus_night": {
                "black": "#010912",
                "white": "#fdeeec",
                "grey": "#051d40",
                "darkgrey": "#091842",
                "lightgrey": "#062151",
                "gray": "#051d40",
                "darkgray": "#091842",
                "lightgray": "#062151",
                "red": "#ad4576",
                "darkred": "#934765",
                "lightred": "#ab6290",
                "brown": "#61646b",
                "darkbrown": "#3d2d2d",
                "lightbrown": "#8393a0",
                "orange": "#0a2227",
                "yellow": "#0a2541",
                "green": "#75ac8d",
                "darkgreen": "#0a2434",
                "lightgreen": "#061f2e",
                "blue": "#0b2c79",
                "lightblue": "#809ccb",
                "darkblue": "#08153b",
                "purple": "#666a87",
                "pink": "#754b4d",
            },
            "proteus_rich": {
                "black": "#6f686f",
                "white": "#d1b1e2",
                "grey": "#b9aac1",
                "darkgrey": "#8e8b84",
                "lightgrey": "#c7b5cd",
                "gray": "#b9aac1",
                "darkgray": "#8e8b84",
                "lightgray": "#c7b5cd",
                "red": "#a11f4f",
                "darkred": "#934765",
                "lightred": "#c998ad",
                "brown": "#89867d",
                "darkbrown": "#797f75",
                "lightbrown": "#ab9997",
                "orange": "#ce8c5c",
                "yellow": "#f0d959",
                "green": "#75bc54",
                "darkgreen": "#599d79",
                "lightgreen": "#90cf5c",
                "blue": "#8fd0ec",
                "lightblue": "#bcdce7",
                "darkblue": "#0b2c70",
                "purple": "#9b377f",
                "pink": "#cd88e5",
            },
            "amstrad": {
                "black": "#000000",
                "white": "#ffffff",
                "grey": "#7f7f7f",
                "darkgrey": "#636363",
                "lightgrey": "#afafaf",
                "gray": "#7f7f7f",
                "darkgray": "#636363",
                "lightgray": "#afafaf",
                "red": "#ff0000",
                "darkred": "#7f0000",
                "lightred": "#ff7f7f",
                "brown": "#ff7f00",
                "darkbrown": "#7f7f00",
                "lightbrown": "#ffff00",
                "orange": "#ff007f",
                "yellow": "#ffff7f",
                "green": "#01ff00",
                "darkgreen": "#007f00",
                "lightgreen": "#7fff7f",
                "blue": "#0000ff",
                "lightblue": "#7f7fff",
                "darkblue": "#00007f",
                "purple": "#7f007f",
                "pink": "#ff7fff",
            },
            "c64": {
                "black": "#000000",
                "white": "#ffffff",
                "grey": "#6C6C6C",
                "darkgrey": "#444444",
                "lightgrey": "#959595",
                "gray": "#6C6C6C",
                "darkgray": "#444444",
                "lightgray": "#959595",
                "red": "#68372B",
                "darkred": "#3f1e17",
                "lightred": "#9A6759",
                "brown": "#433900",
                "darkbrown": "#221c02",
                "lightbrown": "#6d5c0d",
                "orange": "#6F4F25",
                "yellow": "#B8C76F",
                "green": "#588D43",
                "darkgreen": "#345129",
                "lightgreen": "#9AD284",
                "blue": "#6C5EB5",
                "lightblue": "#70A4B2",
                "darkblue": "#352879",
                "purple": "#6F3D86",
                "pink": "#b044ac",
            },
            "whitingjp": {
                "black": "#202527",
                "white": "#eff8fd",
                "grey": "#7b7680",
                "darkgrey": "#3c3b44",
                "lightgrey": "#bed0d7",
                "gray": "#7b7680",
                "darkgray": "#3c3b44",
                "lightgray": "#bed0d7",
                "red": "#bd194b",
                "darkred": "#6b1334",
                "lightred": "#ef2358",
                "brown": "#b52e1c",
                "darkbrown": "#681c12",
                "lightbrown": "#e87b45",
                "orange": "#ff8c10",
                "yellow": "#fbd524",
                "green": "#36bc3c",
                "darkgreen": "#317610",
                "lightgreen": "#8ce062",
                "blue": "#3f62c6",
                "lightblue": "#57bbe0",
                "darkblue": "#2c2fa0",
                "purple": "#7037d9",
                "pink": "#ec2b8f",
            },
        }
        palette_name_list = [
            "mastersystem",
            "gameboycolour",
            "amiga",
            "arnecolors",
            "famicom",
            "atari",
            "pastel",
            "ega",
            "amstrad",
            "proteus_mellow",
            "proteus_rich",
            "proteus_night",
            "c64",
            "whitingjp",
        ]
        if palette_name.isdigit():
            try:
                palette_name = palette_name_list[int(palette_name) - 1]
            except IndexError:
                pass
        palette = color_palettes.get(
            palette_name, color_palettes["arnecolors"]
        )
        palette["transparent"] = "#00000000"
        if color[0] != "#":
            if color in palette:
                color = palette[color]
        return ImageColor.getcolor(color, "RGBA")

    def __create_tileset_xml(self, tileset, size=5):
        tileset_tag = ElementTree.Element("tileset")
        tileset_tag.set("tiledversion", "1.10.1")
        tileset_tag.set("name", "psbs_generated_tileset")
        tileset_tag.set("tilewidth", str(size))
        tileset_tag.set("tileheight", str(size))
        tileset_tag.set("tilecount", str(len(tileset)))
        tileset_tag.set("columns", "0")
        grid_tag = ElementTree.SubElement(tileset_tag, "grid")
        grid_tag.set("orientation", "orthogonal")
        grid_tag.set("width", "1")
        grid_tag.set("height", "1")
        tiles = []
        for tile in tileset:
            tiles.append(ElementTree.SubElement(tileset_tag, "tile"))
            tiles[tile["id"]].set("id", str(tile["id"]))
            properties = ElementTree.SubElement(
                tiles[tile["id"]], "properties"
            )
            property_tag = ElementTree.SubElement(properties, "property")
            property_tag.set("name", "glyph")
            property_tag.set("value", str(tile["glyph"]))
            image_tag = ElementTree.SubElement(tiles[tile["id"]], "image")
            image_tag.set("width", str(size))
            image_tag.set("height", str(size))
            image_tag.set("source", str(tile["filename"]))

        xml_as_string = ElementTree.tostring(tileset_tag, encoding="utf-8")
        parsed_xml = minidom.parseString(xml_as_string)
        pretty_xml = parsed_xml.toprettyxml(indent="  ")
        return pretty_xml

    def write_tileset_files(self, input_str):
        parser = PSParser(input_str)
        sprite_size = 5
        if "sprite_size" in parser.prelude_options:
            if parser.prelude_options["sprite_size"].isdigit():
                sprite_size = int(parser.prelude_options["sprite_size"])
        color_palette = parser.prelude_options.get(
            "color_palette", "arnecolors"
        )
        if not self.config["generate_tileset"]:
            return input_str
        print("Creating tileset")
        tileset_dir = path.join("bin", "tileset")
        images_dir = path.join(tileset_dir, "images")
        if not path.exists(tileset_dir):
            print("tileset directory does not exist, creating one")
            make_dir(tileset_dir)
        if path.exists(images_dir):
            shutil.rmtree(images_dir)
        make_dir(images_dir)
        try:
            tiles = parser.get_glyphs()
        except PSParser.ParseError as err:
            print(f"Warning: unable to create tileset\n  {err}")
            return input_str
        tile_id = 0
        tileset = []
        for glyph, ps_objects in tiles.items():
            image = self.__object_to_pixels(
                ps_objects[0], sprite_size, palette_name=color_palette
            )
            if len(ps_objects) > 0:
                for overlay in ps_objects[1:]:
                    image.paste(
                        self.__object_to_pixels(
                            overlay, sprite_size, palette_name=color_palette
                        ),
                        (0, 0),
                        self.__object_to_pixels(
                            overlay, sprite_size, palette_name=color_palette
                        ),
                    )
            try:
                image.save(path.join(images_dir, f"{tile_id}.png"))
            except IOError as err:
                raise PSBSError(
                    f"Error: Unable to write image {tile_id}.png\n  {err}"
                ) from err
            tileset.append(
                {
                    "glyph": glyph,
                    "id": tile_id,
                    "filename": path.join("images", f"{tile_id}.png"),
                }
            )
            tile_id += 1
        write_file(
            path.join(tileset_dir, "tileset.tsx"),
            self.__create_tileset_xml(tileset, sprite_size),
        )
        return input_str

    def parse_level(self, file):
        try:
            level_xml = ElementTree.parse(file)
        except IOError as err:
            print(f"Warning: Unable to read level file\n  {err}")
            return ""
        source = level_xml.getroot()[0].attrib["source"]
        level_csv = level_xml.getroot()[1][0].text
        tileset_file = path.abspath(path.join(path.dirname(file), source))
        try:
            tileset_xml = ElementTree.parse(tileset_file)
        except IOError as err:
            print(f"Warning: Unable to read tileset file\n  {err}")
            return ""
        tileset = {}
        for child in tileset_xml.getroot():
            if child.tag == "tile":
                try:
                    tileset[child.attrib["id"]] = child[0][0].attrib["value"]
                except (KeyError, IndexError):
                    print("Warning: Incompatible level file")
                    return ""
        output = ""
        if level_csv is not None:
            level_lines = level_csv.strip().split(",\n")
            for line in level_lines:
                level_tiles = line.split(",")
                for tile in level_tiles:
                    output += tileset[str(int(tile) - 1)]
                output += "\n"
        return output

import re


class PSParser:
    def __init__(self, source):
        self.source = source
        self.source_tree = self.split_ps()
        self.sections = {}
        for section, content in self.source_tree.items():
            self.sections[section] = PSParser.__clean("\n".join(content))
        self.prelude_options = {}
        for line in self.sections["prelude"].splitlines():
            tokens = line.split(maxsplit=1)
            if len(tokens) == 1:
                self.prelude_options[tokens[0]] = True
            if len(tokens) == 2:
                self.prelude_options[tokens[0]] = tokens[1]

    @staticmethod
    def __redact_comments(input_str, redact_char=" "):
        depth = 0
        output = ""
        for character in input_str:
            if character == "(":
                depth += 1
            if depth > 0 and character != "\n":
                output += redact_char
            else:
                output += character
            if character == ")":
                depth -= 1
            depth = max(depth, 0)
        return output

    @staticmethod
    def __clean(input_str):
        input_str = PSParser.__redact_comments(input_str, redact_char="")
        output = "\n".join([line.strip() for line in input_str.splitlines()])
        return output

    @staticmethod
    def get_engine(input_str):
        match = re.search(r"(http.*)(?:editor\.html)", input_str)
        return match.group(1) if match else "https://www.puzzlescript.net/"

    def split_ps(self):
        sections = {
            "prelude": [],
            "tags": [],
            "mappings": [],
            "objects": [],
            "legend": [],
            "sounds": [],
            "collisionlayers": [],
            "rules": [],
            "winconditions": [],
            "levels": [],
        }
        optional_sections = ["tags", "mappings"]
        section_headers = list(sections.keys())[1:]
        headers = re.finditer(
            r"^(" + "|".join(section_headers) + ") *$",
            PSParser.__redact_comments(self.source),
            flags=re.IGNORECASE | re.MULTILINE,
        )

        section = "prelude"
        start = 0
        for header in headers:
            content = self.source[start : header.span()[0]]
            content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
            sections[section].append(content.strip())
            section = header.group().strip().lower()
            start = header.span()[1]
        content = self.source[start:]
        content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
        sections[section].append(content.strip())
        for optional_section in optional_sections:
            if not sections[optional_section]:
                del sections[optional_section]

        return sections

    def get_objects(self):
        object_strs = re.split(
            r"(?<=\S)\n+\n+(?=\S)", self.sections["objects"]
        )
        ps_objects = {}
        for object_str in object_strs:
            object_str_lines = object_str.splitlines()
            object_name = object_str_lines[0]
            object_body = object_str_lines[1:]
            ps_objects[object_name] = "\n".join(object_body)
        return ps_objects

    def get_collision_order(self):
        collisionlayers = self.sections["collisionlayers"]
        legend = self.sections["legend"]

        composite_matches = re.finditer(
            r"^(\S+) += +(\S+ +or +\S+(?: +or +\S+)*)$",
            legend,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        composite_objects = {}
        for match in composite_matches:
            composite_objects[match.group(1)] = [
                x.strip() for x in match.group(2).split(" or ")
            ]
        collision_order = re.split(
            r",\s*|\s+", collisionlayers, flags=re.MULTILINE
        )
        collision_order = list(filter(None, collision_order))
        while len([i for i in composite_objects if i in collision_order]) > 0:
            fixed_collision_order = []
            for collision_object in collision_order:
                if collision_object in composite_objects:
                    for composite_component in composite_objects[
                        collision_object
                    ]:
                        fixed_collision_order.append(composite_component)
                else:
                    fixed_collision_order.append(collision_object)
            collision_order = fixed_collision_order
        return collision_order

    def get_tiles(self):
        # This function is a mess, please clean it up
        legend = self.sections["legend"]
        ps_objects = self.get_objects()
        collision_order = self.get_collision_order()
        prelude = self.prelude_options

        # get the name of the Background object in case of case_sensitive
        background_name = "background"
        for object_name in ps_objects:
            if object_name.lower() == "background":
                background_name = object_name

        if "case_sensitive" not in prelude:
            background_name = background_name.lower()
            ps_objects = {
                key.lower(): value for key, value in ps_objects.items()
            }
            collision_order = list(map(str.lower, collision_order))
            legend = legend.lower()

        tiles = {}
        tile_matches = re.finditer(
            r"^(\S) += +((?:(?! or ).)*)$",
            legend,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        for match in tile_matches:
            tiles[match.group(1)] = re.split(
                " and ", match.group(2), flags=re.IGNORECASE
            )
        for name, body in ps_objects.copy().items():
            tokens_in_name = name.split()
            if len(tokens_in_name) > 0:
                ps_objects[tokens_in_name[0]] = ps_objects.pop(name)
                for tile_token in tokens_in_name[1:]:
                    if len(tile_token) == 1:
                        tiles[tile_token] = [tokens_in_name[0]]
                    elif tile_token.startswith("copy:"):
                        # handle PuzzleScript+ copy feature
                        ps_objects[tokens_in_name[0]] = "\n".join(
                            body.splitlines()[:1]
                            + ps_objects[tile_token[5:]].splitlines()[1:]
                        )
        for glyph, name in tiles.items():
            if len(name) == 1:
                if name[0] in collision_order:
                    collision_order.insert(
                        collision_order.index(name[0]), glyph
                    )
                elif glyph in collision_order:
                    collision_order.insert(
                        collision_order.index(glyph), name[0]
                    )
                if name[0] in ps_objects:
                    ps_objects[glyph] = ps_objects[name[0]]
        for tile in tiles.values():
            if background_name not in tile:
                tile.append(background_name)

        for tile_key in tiles:
            tiles[tile_key] = sorted(
                tiles[tile_key], key=collision_order.index
            )
        graphical_tiles = {}
        for glyph, names in tiles.items():
            graphical_tiles[glyph] = []
            for name in names:
                graphical_tiles[glyph].append(ps_objects[name])
        return graphical_tiles

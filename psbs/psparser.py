import re


def redact(input_str, redact_char=" "):
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
        if depth < 0:
            depth = 0
    return output


def clean(input_str):
    input_str = redact(input_str, redact_char="")
    output = "\n".join([line.strip() for line in input_str.splitlines()])
    return output


def split_ps(input_str):
    input_redacted = redact(input_str)
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
        input_redacted,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    section = "prelude"
    start = 0
    for header in headers:
        content = input_str[start : header.span()[0]]
        content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
        sections[section].append(content.strip())
        section = header.group().strip().lower()
        start = header.span()[1]
    content = input_str[start:]
    content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
    sections[section].append(content.strip())
    for optional_section in optional_sections:
        if not sections[optional_section]:
            del sections[optional_section]

    return sections


def get_engine(input_str):
    match = re.search(r"(http.*)(?:editor\.html)", input_str)
    if match is None:
        output = "https://www.puzzlescript.net/"
    else:
        output = match.group(1)
    return output


def get_section(input_str, section_name, clean_output=True):
    output = "\n".join(split_ps(input_str)[section_name])
    if clean_output:
        return clean(output)
    return output

def get_prelude_options(input_str):
    prelude_options = {}
    prelude_str = get_section(input_str, "prelude")
    for line in prelude_str.splitlines():
        tokens = line.split(maxsplit=1)
        if len(tokens) == 1:
            prelude_options[tokens[0]] = True
        if len(tokens) == 2:
            prelude_options[tokens[0]] = tokens[1]
    return prelude_options

def get_objects(input_str):
    object_strs = re.split(
        r"(?<=\S)\n+\n+(?=\S)", get_section(input_str, "objects")
    )
    ps_objects = {}
    for object_str in object_strs:
        object_str_lines = object_str.splitlines()
        object_name = object_str_lines[0].lower()
        object_body = object_str_lines[1:]
        ps_objects[object_name] = "\n".join(object_body)

    return ps_objects


def get_collision_order(input_str):
    collisionlayers = get_section(input_str, "collisionlayers")
    legend = get_section(input_str, "legend")

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
    while (
        len([i for i in composite_objects.keys() if i in collision_order]) > 0
    ):
        fixed_collision_order = []
        for collision_object in collision_order:
            if collision_object in composite_objects:
                for composite_component in composite_objects[collision_object]:
                    fixed_collision_order.append(composite_component)
            else:
                fixed_collision_order.append(collision_object)
        collision_order = fixed_collision_order
    collision_order = list(map(str.lower, collision_order))
    return collision_order


def get_tiles(input_str):
    legend = get_section(input_str, "legend").lower()
    ps_objects = get_objects(input_str)
    collision_order = get_collision_order(input_str)
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
                elif tile_token.startswith('copy:'):
                    # handle PuzzleScript+ copy feature
                    ps_objects[tokens_in_name[0]] = "\n".join(body.splitlines()[:1]+ps_objects[tile_token[5:]].splitlines()[1:])
    for glyph, name in tiles.items():
        if len(name) == 1:
            if name[0] in collision_order:
                collision_order.insert(collision_order.index(name[0]), glyph)
            elif glyph in collision_order:
                collision_order.insert(collision_order.index(glyph), name[0])
            if name[0] in ps_objects:
                ps_objects[glyph] = ps_objects[name[0]]
    for tile in tiles.values():
        if "background" not in tile:
            tile.append("background")
    # FIXME: object glyphs can be used in collision layers!
    for tile_key in tiles.keys():
        tiles[tile_key] = sorted(
            tiles[tile_key], key=collision_order.index
        )
    graphical_tiles = {}
    for glyph, names in tiles.items():
        graphical_tiles[glyph] = []
        for name in names:
            graphical_tiles[glyph].append(ps_objects[name])
    return graphical_tiles

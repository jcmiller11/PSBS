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
                self.prelude_options[tokens[0].lower()] = True
            if len(tokens) == 2:
                self.prelude_options[tokens[0].lower()] = tokens[1]

    class ParseError(Exception):
        """Thrown when unable to parse the input PS"""

    @staticmethod
    def __redact_comments(input_str, redact_char=" "):
        depth = 0
        output = ""
        in_a_message = False
        for character in input_str:
            if output[-8:].lower() == "message ":
                in_a_message = True
            if character == "\n":
                in_a_message = False
            if character == "(" and not in_a_message:
                depth += 1
            if depth > 0 and character != "\n" and not in_a_message:
                output += redact_char
            else:
                output += character
            if character == ")" and not in_a_message:
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
            try:
                object_str_lines = object_str.splitlines()
                name = object_str_lines.pop(0)
                if "case_sensitive" not in self.prelude_options:
                    name = name.lower()
                colors = object_str_lines.pop(0)
                body = "\n".join(object_str_lines)
                # ps_objects[object_name] = body
                # consider using dict:
                synonyms = []
                tokens_in_name = name.split()
                if len(tokens_in_name) > 0:
                    name = tokens_in_name.pop(0)
                    for token in tokens_in_name:
                        if token.startswith("copy:"):
                            # handle PuzzleScript+ copy feature
                            body = ps_objects[token[5:]]["body"]
                        else:
                            synonyms.append(token)
                ps_objects[name] = {
                    "colors": colors,
                    "body": body,
                    "synonyms": synonyms,
                }
            except IndexError:
                print("Warning: unable to parse object:")
                print(object_str)
        return ps_objects

    def get_glyphs(self):
        # Code Smell: this method is way too long, consider breaking
        # it up in the future however it's working pretty well for now
        legend = self.sections["legend"]
        ps_objects = self.get_objects()
        collisionlayers = self.sections["collisionlayers"]

        # handle case sensitivity
        background_name = "background"
        for object_name in ps_objects:
            if object_name.lower() == "background":
                background_name = object_name
        if "case_sensitive" not in self.prelude_options:
            legend = legend.lower()
            collisionlayers = collisionlayers.lower()

        synonyms = {}
        properties = {}  # Properties apply to collisionlayers
        aggregates = {}  # Aggregates apply to glyphs
        matches = re.finditer(
            r"^(\S+) += +(\S+(?: +(?:and|or) +\S+)*)$",
            legend,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        for match in matches:
            if " and " in match.group(2):
                aggregates[match.group(1)] = re.split(
                    r" +and +", match.group(2), flags=re.IGNORECASE
                )
            elif " or " in match.group(2):
                properties[match.group(1)] = re.split(
                    r" +or +", match.group(2), flags=re.IGNORECASE
                )
            else:
                synonyms[match.group(1)] = match.group(2)
        for ps_object in ps_objects:
            for synonym in ps_objects[ps_object]["synonyms"]:
                synonyms[synonym] = ps_object
            synonyms[ps_object] = ps_object
        # resolve synonyms
        for synonym in synonyms:
            if synonyms[synonym] in synonyms:
                synonyms[synonym] = synonyms[synonyms[synonym]]

        def resolve_dict(input_dict):
            must_recurse = True
            output = {}
            while must_recurse:
                # This can loop forever if there are circular references
                # consider adding a max number of loops
                must_recurse = False
                output = {}
                for key in input_dict:
                    output[key] = []
                    for object_name in input_dict[key]:
                        if object_name in input_dict:
                            for inner_key in input_dict[object_name]:
                                if inner_key in synonyms:
                                    output[key].append(synonyms[inner_key])
                                else:
                                    output[key].append(inner_key)
                        else:
                            if object_name in synonyms:
                                output[key].append(synonyms[object_name])
                            else:
                                output[key].append(object_name)
                for key in output:
                    for object_name in output[key]:
                        if object_name in output:
                            must_recurse = True
                input_dict = output
            return output

        properties = resolve_dict(properties)
        aggregates = resolve_dict(aggregates)

        glyphs = {}
        for synonym in synonyms:
            if len(synonym) == 1:
                if synonyms[synonym] in aggregates:
                    glyphs[synonym] = aggregates[synonyms[synonym]]
                else:
                    glyphs[synonym] = [synonyms[synonym]]

        for aggregate in aggregates:
            if len(aggregate) == 1:
                glyphs[aggregate] = aggregates[aggregate]

        collision_order = []
        for collision_object in re.split(
            r",\s*|\s+", collisionlayers, flags=re.MULTILINE
        ):
            if collision_object in properties:
                for inner_object in properties[collision_object]:
                    if inner_object in synonyms:
                        collision_order.append(synonyms[inner_object])
                    else:
                        collision_order.append(inner_object)
            else:
                if collision_object in synonyms:
                    collision_order.append(synonyms[collision_object])
                else:
                    collision_order.append(collision_object)

        for glyph in glyphs:
            if background_name not in glyphs[glyph]:
                glyphs[glyph].append(background_name)
            try:
                glyphs[glyph] = sorted(
                    glyphs[glyph], key=collision_order.index
                )
            except ValueError as err:
                raise self.ParseError(
                    f"Can't find object in collisionlayers:\n  {err}"
                )
            glyph_objects = []
            for object_name in glyphs[glyph]:
                glyph_objects.append(
                    "\n".join(
                        [
                            ps_objects[object_name]["colors"],
                            ps_objects[object_name]["body"],
                        ]
                    ).strip()
                )
            glyphs[glyph] = glyph_objects
        return glyphs

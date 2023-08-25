import re


class PSParser:
    def __init__(self, source):
        self.source = source
        self.source_tree = self.split_ps()
        self.sections = {
            section: PSParser.__clean("\n".join(content))
            for section, content in self.source_tree.items()
        }
        self.prelude_options = self.__parse_prelude(self.sections["prelude"])

    @staticmethod
    def __parse_prelude(prelude_section):
        prelude_options = {}
        for line in prelude_section.splitlines():
            tokens = line.split(maxsplit=1)
            if len(tokens) == 1:
                prelude_options[tokens[0].lower()] = True
            elif len(tokens) == 2:
                prelude_options[tokens[0].lower()] = tokens[1]
        return prelude_options

    class ParseError(Exception):
        """Thrown when unable to parse the input PS"""

    @staticmethod
    def redact_comments(input_str, redact_char=" "):
        depth = 0
        output = []
        in_a_message = False
        for character in input_str:
            if len(output) > 8 and "".join(output[-8:]).lower() == "message ":
                in_a_message = True
            if character == "\n":
                in_a_message = False
            if character == "(" and not in_a_message:
                depth += 1
            if depth > 0 and character != "\n" and not in_a_message:
                output.append(redact_char)
            else:
                output.append(character)
            if character == ")" and not in_a_message:
                depth = max(depth - 1, 0)
        return "".join(output)

    @staticmethod
    def __clean(input_str):
        input_str = PSParser.redact_comments(input_str, redact_char="")
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
            PSParser.redact_comments(self.source),
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
        # Retrieve relevant sections and objects
        legend = self.sections["legend"]
        ps_objects = self.get_objects()
        collisionlayers = self.sections["collisionlayers"]

        synonyms = {}  # Dictionary to store synonyms
        properties = {}  # Properties apply to collisionlayers
        aggregates = {}  # Aggregates apply to glyphs

        # Handle case sensitivity
        background_name = next(
            (obj for obj in ps_objects if obj.lower() == "background"),
            "background",
        )
        if "case_sensitive" not in self.prelude_options:
            legend = legend.lower()
            collisionlayers = collisionlayers.lower()

        # Extract information from the legend section
        for key, values in re.findall(
            r"^(\S+) += +(\S+(?: +(?:and|or) +\S+)*)$",
            legend,
            flags=re.MULTILINE | re.IGNORECASE,
        ):
            if " and " in values:
                aggregates[key] = re.split(
                    r" +and +", values, flags=re.IGNORECASE
                )
            elif " or " in values:
                properties[key] = re.split(
                    r" +or +", values, flags=re.IGNORECASE
                )
            else:
                synonyms[key] = values

        # Populate synonyms using ps_objects data
        synonyms.update(
            {
                synonym: key
                for key, value in ps_objects.items()
                for synonym in value["synonyms"]
            }
        )
        synonyms.update({ps_object: ps_object for ps_object in ps_objects})

        # Resolve synonyms
        synonyms = {
            synonym: synonyms.get(synonym, synonym) for synonym in synonyms
        }

        # Resolve properties and aggregates using synonyms
        properties = self.__resolve_dict(properties, synonyms)
        aggregates = self.__resolve_dict(aggregates, synonyms)

        # Create glyphs dictionary
        glyphs = {
            synonym: aggregates.get(synonyms[synonym], [synonyms[synonym]])
            for synonym in synonyms
            if len(synonym) == 1
        }

        # Update glyphs dictionary with single-character aggregates
        glyphs.update(
            {key: value for key, value in aggregates.items() if len(key) == 1}
        )

        # Build collision order based on resolved synonyms and properties
        collision_order = [
            synonyms.get(inner_object, inner_object)
            for collision_object in re.split(
                r",\s*|\s+", collisionlayers, flags=re.MULTILINE
            )
            for inner_object in properties.get(
                collision_object, [collision_object]
            )
        ]

        # Construct glyph objects with resolved properties and order
        for glyph in glyphs:
            if background_name not in glyphs[glyph]:
                glyphs[glyph].append(background_name)
            try:
                glyphs[glyph].sort(key=collision_order.index)
            except ValueError as err:
                raise self.ParseError(
                    f"Can't find object in collisionlayers:\n  {err}"
                )

            glyphs[glyph] = [
                "\n".join(
                    [
                        ps_objects[object_name]["colors"],
                        ps_objects[object_name]["body"],
                    ]
                ).strip()
                for object_name in glyphs[glyph]
            ]
        return glyphs

    @staticmethod
    def __resolve_dict(input_dict, synonyms=None):
        output = {}

        while True:  # Continue resolving until no changes occur
            changed = False

            # Iterate through items in the input_dict
            for key, values in input_dict.items():
                resolved_values = []

                # Iterate through values of the current key
                for value in values:
                    if value in input_dict:
                        resolved_values.extend(input_dict[value])
                        changed = True
                    elif synonyms:
                        # Use synonyms if value is not in input_dict
                        resolved_values.append(synonyms.get(value, value))

                output[key] = resolved_values

            # If no changes occurred in this iteration, exit the loop
            if not changed:
                return output

            # Set input_dict to output to continue with updated values
            input_dict = output

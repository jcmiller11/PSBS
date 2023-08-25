"""
PSPARSER

This file provides the PSParser class for parsing and processing
PuzzleScript source code.
"""

import re

class PSParser:
    """
    A class for parsing and processing PuzzleScript source code.

    This class provides methods for extracting information from various
    sections of PuzzleScript source code.
    It can parse sections like prelude, objects, legend, collisionlayers.

    Attributes:
        source (str): The input PuzzleScript source code.
        source_tree (dict): A dictionary containing parsed sections of the
        PuzzleScript source.
        sections (dict): A dictionary containing cleaned content of each
        section in the PuzzleScript source.
        prelude_options (dict): A dictionary containing prelude options and
        their values.

    Methods:
        get_engine(input_str): Extracts the engine URL from the input readme
        file.
        split_ps(self): Splits the PuzzleScript source code into different
        sections.
        get_objects(self): Extracts and parses objects from the 'objects'
        section of PuzzleScript source.
        get_glyphs(self): Extracts and organizes glyphs and their associated
        sprite data.
    """
    def __init__(self, source):
        self.source = source
        self.source_tree = self.split_ps()

        # Extract and clean the content of each section
        self.sections = {
            section: PSParser.__clean("\n".join(content))
            for section, content in self.source_tree.items()
        }

        # Parse the prelude section to extract options
        self.prelude_options = self.__parse_prelude(self.sections["prelude"])

    @staticmethod
    def __parse_prelude(prelude_section):
        """
        Parse the prelude section of a PuzzleScript source file.

        Args:
            prelude_section (str): The content of the prelude section.

        Returns:
            dict: A dictionary containing the prelude options and their values.
        """
        prelude_options = {}
        # Split the prelude section into lines and process each line.
        for line in prelude_section.splitlines():
            tokens = line.split(maxsplit=1)
            if len(tokens) == 1:
                # If there's only one token, set the option to True.
                prelude_options[tokens[0].lower()] = True
            elif len(tokens) == 2:
                # If there are two tokens, set the option to the provided value.
                prelude_options[tokens[0].lower()] = tokens[1]
        return prelude_options

    class ParseError(Exception):
        """Thrown when unable to parse the input PS"""

    @staticmethod
    def redact_comments(input_str, redact_char=" "):
        """
        Redact comments from a PuzzleScript source code while preserving
        message content.

        Args:
            input_str (str): The input PuzzleScript source code.
            redact_char (str, optional): The character used for redacting
                comments. Defaults to " ".

        Returns:
            str: The input source code with comments redacted.
        """
        depth = 0 # Number to track depth of nested comments
        output = []
        in_a_message = False

        # Iterate through each character in the input source code.
        for character in input_str:
            # Check if the last 8 characters are "message " to identify if
            # we are currently inside a message.
            if len(output) > 8 and "".join(output[-8:]).lower() == "message ":
                in_a_message = True

            # When a newline is encountered, we are no longer in a message.
            if character == "\n":
                in_a_message = False

            # If an opening parenthesis is encountered and we are not inside a
            # message, increment the depth.
            if character == "(" and not in_a_message:
                depth += 1

            # If the depth is greater than 0 and the character is not a
            # newline and we are not inside a message, append the redact_char
            # to the output list.
            if depth > 0 and character != "\n" and not in_a_message:
                output.append(redact_char)
            else:
                # If none of the above conditions are met, append the character
                # to the output list.
                output.append(character)

            # When a closing parenthesis is encountered and we are not inside a
            # message, decrement the depth, ensuring it stays non-negative.
            if character == ")" and not in_a_message:
                depth = max(depth - 1, 0)

        return "".join(output)

    @staticmethod
    def __clean(input_str):
        """
        Clean the input source code by redacting comments and removing extra
        whitespace.

        Args:
            input_str (str): The input source code.

        Returns:
            str: The cleaned source code.
        """
        # Redact comments using the redact_comments method from PSParser class.
        input_str = PSParser.redact_comments(input_str, redact_char="")

        # Join the cleaned lines after stripping leading and trailing whitespace.
        output = "\n".join([line.strip() for line in input_str.splitlines()])
        return output

    @staticmethod
    def get_engine(input_str):
        """
        Extract the engine URL from the input readme file.

        Args:
            input_str (str): Text of the input readme file.

        Returns:
            str: The extracted engine URL or a default URL if not found.
        """
        # Use regular expression to search for an engine URL pattern in the input.
        match = re.search(r"(http.*)(?:editor\.html)", input_str)

        # If a match is found, return the captured group (engine URL).
        # Otherwise, return the default PuzzleScript engine URL.
        return match.group(1) if match else "https://www.puzzlescript.net/"

    def split_ps(self):
        """
        Split the PuzzleScript source code into different sections based on section headers.

        Returns:
            dict: A dictionary containing parsed sections of the PuzzleScript source.

        Example:
            ps_parser = PSParser(source)
            sections = ps_parser.split_ps()
            print(sections['objects'])  # Print the 'objects' section content.
        """
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

       # Splitting the source into sections based on section headers
        section_headers = list(sections.keys())[1:]
        headers = re.finditer(
            r"^(" + "|".join(section_headers) + ") *$",
            PSParser.redact_comments(self.source),
            flags=re.IGNORECASE | re.MULTILINE,
        )

        # Extract content for each section
        section = "prelude"
        start = 0
        for header in headers:
            content = self.source[start : header.span()[0]]
            content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
            sections[section].append(content.strip())
            section = header.group().strip().lower()
            start = header.span()[1]
        # Extract content for the last section
        content = self.source[start:]
        content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
        sections[section].append(content.strip())

        # Remove optional sections if they are empty
        for optional_section in ["tags", "mappings"]:
            if not sections[optional_section]:
                del sections[optional_section]

        return sections

    def get_objects(self):
        """
        Extract and parse objects from the 'objects' section of PuzzleScript
        source.

        Returns:
            dict: A dictionary containing parsed objects, their properties,
            and synonyms.
        """
        # Split the 'objects' section into individual object strings
        object_strs = re.split(
            r"(?<=\S)\n+\n+(?=\S)", self.sections["objects"]
        )

        # Dictionary to store parsed objects
        ps_objects = {}

        for object_str in object_strs:
            try:
                # Split object string into lines
                name, colors, *body = object_str.splitlines()

                # Join the remaining lines to form the body
                body = "\n".join(body)
                synonyms = []

                # Handle case_sensitive prelude option by converting object
                # name to lowercase if source is case insensitive
                if "case_sensitive" not in self.prelude_options:
                    name = name.lower()

                # Split the object name to get name and potential synonyms
                tokens_in_name = name.split()
                name = tokens_in_name[0]
                for token in tokens_in_name[1:]:
                    if token.startswith("copy:"):
                        # Handle PuzzleScript+ copy feature
                        body = ps_objects[token[5:]]["body"]
                    else:
                        synonyms.append(token)

                # Store parsed object with its properties in the dictionary
                ps_objects[name] = {
                    "colors": colors,
                    "body": body,
                    "synonyms": synonyms,
                }
            # Handle incomplete object strings
            except IndexError:
                print("Warning: unable to parse object:")
                print(object_str)

        return ps_objects

    def get_glyphs(self):
        """
        Extract and organize glyphs and their associated sprite data based on
        PuzzleScript legend, objects, and collisionlayers.

        Returns:
            dict: A dictionary containing glyph definitions with resolved
            properties and order.
        """
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
        """
        Private utility method to recursively resolve references in a dictionary.

        This method recursively resolves synonyms in a given dictionary. It
        iterates through the dictionary, replacing values with their
        corresponding values from synonyms or from the dictionary itself.

        Args:
            input_dict (dict): The dictionary to be resolved.
            synonyms (dict, optional): A dictionary containing synonym mappings.
            Defaults to None.

        Returns:
            dict: The resolved dictionary with synonyms replaced by their
            corresponding values.
        """
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

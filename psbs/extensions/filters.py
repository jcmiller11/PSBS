"""
FILTERS EXTENSION

This file provides an extension class that provides various filters for use
within PSBS Templates.
"""

import re
from textwrap import wrap
from itertools import chain

from psbs.extension import Extension
from psbs.psparser import PSParser


class Filters(Extension):
    """
    A class representing a filters extension for PSBS.

    This extension provides various filters that can be applied to text or
    level data.

    Args:
        config (dict): A configuration dictionary for the extension.

    Attributes:
        config (dict): The configuration dictionary for the extension.

    Methods:
        wrap_to_width(input_text, width=5): Wrap text to a specified width.
        add_prefix(input_text, prefix): Add a prefix to each non-empty line.
        levels_to_list(levels_string): Convert string of levels to a list.
        combine_levels(levels_list, columns=0): Combine levels into rows.
    """

    def __init__(self, config):
        super().__init__(config)
        self.register_filter("wrap", self.wrap_to_width)
        self.register_filter("add_prefix", self.add_prefix)
        self.register_filter("levels_to_list", self.levels_to_list)
        self.register_filter("combine_levels", self.combine_levels)

    def wrap_to_width(self, input_text, width=5):
        """
        Wrap text to a specified width.

        Args:
            input_text (str): The input text to be wrapped.
            width (int, optional): The maximum width for each line.
                Defaults to 5.

        Returns:
            str: The wrapped text.
        """
        wrapped_lines = []
        for line in input_text.splitlines():
            wrapped_lines.extend(wrap(line, width))
        return "\n".join(wrapped_lines)

    def add_prefix(self, input_text, prefix):
        """
        Add a prefix to each non-empty line.

        Args:
            input_text (str): The input text to which the prefix will be added.
            prefix (str): The prefix to be added.

        Returns:
            str: The text with the specified prefix added to non-empty lines.
        """
        input_text = PSParser.redact_comments(input_text, redact_char="")
        output = []
        for line in input_text.splitlines():
            if line.strip() == "":
                # Don't add prefix if line is empty
                output.append("")
            else:
                output.append(f"{prefix} {line}")
        return "\n".join(output)

    def levels_to_list(self, levels_string):
        """
        Convert levels in string format to a list of levels.

        Args:
            levels_string (str): The levels in string format.

        Returns:
            list: A list of levels.
        """
        levels_string = PSParser.redact_comments(levels_string, redact_char="")
        output = []
        for line in levels_string.splitlines():
            # Remove messages from output
            output.append(line.split("message")[0].strip())
        return re.split(r"(?<=\S)\n+\n+(?=\S)", "\n".join(output))

    def combine_levels(self, levels_list, columns=0):
        """
        Combine levels into rows.

        Args:
            levels_list (str or list): The levels to be combined.
            columns (int, optional): Number of columns for combining levels.
                Defaults to 0.

        Returns:
            str: The combined levels.
        """
        if isinstance(levels_list, str):
            # Convert to list if passed a string
            levels_list = self.levels_to_list(levels_list)
        try:
            # In case we get passed some other kind of iterable
            levels_list = list(levels_list)
        except TypeError as err:
            raise self.ExtensionError(err)

        if isinstance(levels_list[0], list):
            # Flatten 2D list if the user asks for a specific number of columns
            levels_list = (
                list(chain(*levels_list)) if columns > 0 else levels_list
            )
            rows = levels_list
        else:
            # If there is only one row then the entire levels list will be it
            rows = [levels_list]

        if columns > 0:
            # Break up list into rows by number of columns
            rows = list(
                levels_list[pos : pos + columns]
                for pos in range(0, len(levels_list), columns)
            )

        def combine_row(input_list):
            level_lines = []
            for level in input_list:
                level = level.strip()
                for line_number, line in enumerate(level.splitlines()):
                    line = line.strip()
                    if len(level_lines) <= line_number:
                        level_lines.append(line)
                    else:
                        level_lines[line_number] += line
            return "\n".join(level_lines)

        return "\n".join([combine_row(row) for row in rows])

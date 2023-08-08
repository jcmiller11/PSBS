import re

from psbs.extension import Extension
from psbs.psparser import PSParser


class Filters(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register_filter("wrap", self.wrap_to_width)
        self.register_filter("levels_to_list", self.levels_to_list)
        self.register_filter("combine_levels", self.combine_levels)

    def wrap_to_width(self, input_text, width=5):
        output = ""
        for line in str(input_text).splitlines():
            output += "\n".join(
                [line[i : i + width] for i in range(0, len(line), width)]
            )
        return output

    def levels_to_list(self, levels_string):
        levels_string = PSParser.redact_comments(levels_string, redact_char="")
        output = ""
        for line in levels_string.splitlines():
            output += line.split("message")[0].strip()
            output += "\n"
        return re.split(
            r"(?<=\S)\n+\n+(?=\S)", output
        )

    def combine_levels(self, levels_list, columns = 0):
        if isinstance(levels_list, str):
            levels_list = self.levels_to_list(levels_list)
        try:
            levels_list = list(levels_list)
        except TypeError as err:
            raise self.ExtensionError(err)
        if isinstance(levels_list[0], list):
            rows = levels_list
        elif columns == 0:
            rows = [levels_list]
        else:
            rows = [levels_list[pos:pos + columns] for pos in range(0, len(levels_list), columns)]
        def combine_row(list):
            level_lines = []
            for level_number, level in enumerate(list):
                level = level.strip()
                for line_number, line in enumerate(level.splitlines()):
                    line = line.strip()
                    if len(level_lines) <= line_number:
                        level_lines.append(line)
                    else:
                        level_lines[line_number] += line
            return level_lines
        output = ""
        for row in rows:
            for line in combine_row(row):
                output += line
                output += "\n"
        return output.strip()

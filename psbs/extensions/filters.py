from psbs.extension import Extension


class Filters(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register_filter("wrap", self.wrap_to_width)
        self.register_filter("combine_levels", self.combine_levels)

    def wrap_to_width(self, input_text, width=5):
        output = ""
        for line in str(input_text).splitlines():
            output += "\n".join(
                [line[i : i + width] for i in range(0, len(line), width)]
            )
        return output

    def combine_levels(self, levels_list, columns = 0):
        if columns == 0:
            columns = len(levels_list)
        rows = (levels_list[pos:pos + columns] for pos in range(0, len(levels_list), columns))
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

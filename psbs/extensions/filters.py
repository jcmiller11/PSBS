from psbs.extension import Extension


class Filters(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register_filter("wrap", self.wrap_to_width)

    def wrap_to_width(self, input, width=5):
        output = ""
        for line in str(input).splitlines():
            output += "\n".join(
                [line[i : i + 5] for i in range(0, len(line), 5)]
            )
        return output

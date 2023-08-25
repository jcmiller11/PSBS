from os import path
import traceback

import jinja2
from .extension import Extension


class Template:
    def __init__(self, filename, config):
        self.file = path.basename(filename)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(path.dirname(filename)),
            autoescape=False,
            block_start_string="(%",
            block_end_string="%)",
            variable_start_string="((",
            variable_end_string="))",
            comment_start_string="(#",
            comment_end_string="#)",
            extensions=["jinja2.ext.do"],
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline = True,
        )
        self.postprocessing_steps = []
        user_extensions = config.get("user_extensions", [])
        extensions = Extension.get_extensions(user_extensions)
        for extension in extensions:
            config.setdefault(extension.__name__, {})
            ext_object = extension(config[extension.__name__])

            self.jinja_env.globals.update(ext_object.methods)
            self.jinja_env.filters.update(ext_object.filters)
            self.postprocessing_steps.extend(ext_object.post)

    def render(self):
        try:
            template = self.jinja_env.get_template(self.file)
            output = template.render()
        except jinja2.exceptions.TemplateNotFound as err:
            print(f"Error: Unable to find template '{err}'")
            raise SystemExit(1) from err
        except (jinja2.exceptions.TemplateError, TypeError) as err:
            print(f"Error: Unable to render template\n  {err}")
            traceback_list = traceback.format_exc().split("\n")
            for index, line in enumerate(traceback_list):
                if line.startswith('  File "src'):
                    print(line)
                    print(traceback_list[index + 1])
                    print(traceback_list[index + 2])
            raise SystemExit(1) from err
        output = self.postprocess(output)
        return output

    def postprocess(self, input_str):
        for post_function in self.postprocessing_steps:
            input_str = post_function(input_str)
        return input_str

    @staticmethod
    def make_template(src_tree):
        lines = []
        for section, content in src_tree.items():
            if section != "prelude":
                lines.extend(
                    [
                        f"{'=' * (len(section) + 1)}",
                        section.upper(),
                        f"{'=' * (len(section) + 1)}",
                    ]
                )
            if not content:
                content = [""]
            for index, _ in enumerate(content, start=1):
                index_str = "" if len(content) == 1 else str(index)
                src_filename = f"{section}{index_str}.pss"
                lines.append(f'(% include "{src_filename}" +%)')
        return "\n".join(lines).strip()

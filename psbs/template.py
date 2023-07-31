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
        )
        self.postprocessing_steps = []
        extensions = Extension.get_extensions()
        for extension in extensions:
            if extension.__name__ not in config:
                config[extension.__name__] = {}
            ext_object = extension(config[extension.__name__])
            for func_name, function in ext_object.methods.items():
                self.jinja_env.globals[func_name] = function
            for function in ext_object.post:
                self.postprocessing_steps.append(function)

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
        output = input_str
        for post_function in self.postprocessing_steps:
            output = post_function(output)
        return output

    @staticmethod
    def make_template(src_tree):
        output = ""
        for section in src_tree:
            if section != "prelude":
                if section != "prelude":
                    output += "=" * (len(section) + 1)
                    output += f"\n{section.upper()}\n"
                    output += "=" * (len(section) + 1)
                    output += "\n\n"
            if not src_tree[section]:
                src_tree[section] = [""]
            for index in range(len(src_tree[section])):
                index += 1
                if len(src_tree[section]) == 1:
                    index = ""
                src_filename = f"{section}{index}.pss"
                output += f'(% include "{src_filename}" %)\n'
            output += "\n"
        return output.strip()

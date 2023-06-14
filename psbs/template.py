from os import path
from sys import modules
import traceback

import jinja2
from psbs.extensions import *
from .extension import Extension


def get_extensions():
    class_list = []
    for module_name, module in modules.items():
        if module_name.startswith("psbs.extensions."):
            for the_class in (
                module_item
                for _, module_item in module.__dict__.items()
                if (
                    isinstance(module_item, type)
                    and module_item.__module__ == module.__name__
                    and issubclass(module_item, Extension)
                )
            ):
                class_list.append(the_class)
    return class_list


def render_template(filename):
    directory = path.dirname(filename)
    file = path.basename(filename)
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(directory),
        autoescape=False,
        block_start_string="(%",
        block_end_string="%)",
        variable_start_string="((",
        variable_end_string="))",
        comment_start_string="(#",
        comment_end_string="#)",
    )
    extensions = get_extensions()
    for extension in extensions:
        ext_object = extension()
        for func_name, function in ext_object.methods.items():
            jinja_env.globals[func_name] = function

    try:
        template = jinja_env.get_template(file)
        return template.render()
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

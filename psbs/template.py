from os import path
import traceback

import jinja2
from .extension import Extension


def render_template(filename, config):
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
    post_processing_steps = []
    extensions = Extension.get_extensions()
    for extension in extensions:
        if extension.__name__ not in config:
            config[extension.__name__] = {}
        ext_object = extension(config[extension.__name__])
        for func_name, function in ext_object.methods.items():
            jinja_env.globals[func_name] = function
        for function in ext_object.post:
            post_processing_steps.append(function)

    try:
        template = jinja_env.get_template(file)
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

    for post_function in post_processing_steps:
        output = post_function(output)

    return output

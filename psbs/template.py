from os import path
import traceback

import jinja2
from .images import image_to_object


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

    jinja_env.globals.update(image=image_to_object)

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

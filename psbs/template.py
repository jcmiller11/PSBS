from os import path
import traceback

import jinja2


def render_template(filename):
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path.dirname(filename)),
        autoescape=False
    )
    try:
        template = jinja_env.get_template(path.basename(filename))
        return template.render()
    except jinja2.exceptions.TemplateNotFound as err:
        print(f"Error: Unable to find template '{err}'")
        raise SystemExit(1) from err
    except jinja2.exceptions.TemplateError as err:
        print(f"Error: Unable to render template\n  {err}")
        print(traceback.format_exc().split('\n')[-5])
        print(traceback.format_exc().split('\n')[-4])
        raise SystemExit(1) from err

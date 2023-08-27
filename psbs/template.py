"""
TEMPLATE MODULE

This module provides a class for rendering PSBS templates with Jinja2.

The Template class in this module offers functionality for rendering Jinja2
templates with PSBS extensions, and post-processing steps.

Example:
    template = Template("my_template.pss", config)
    rendered_output = template.render()

"""

from os import path
import traceback

import jinja2
from .extension import Extension


class Template:
    """
    A class for rendering PSBS templates with Jinja2.

    This class provides functionality for rendering Jinja2 templates with
    PSBS extensions, and post-processing steps.

    Args:
        filename (str): The filename of the main template file.
        config (dict): A configuration dictionary containing extension
        settings.

    Attributes:
        file (str): The basename of the template file.
        jinja_env (jinja2.Environment): The Jinja2 environment with custom
        settings.
        postprocessing_steps (list): A list of post-processing functions.

    Methods:
        render(): Renders the template and applies post-processing.
        postprocess(input_str): Applies post-processing to the input string.
        make_template(src_tree): Generates a template as a string from a
        source tree.
    """

    def __init__(self, filename, config):
        self.file = path.basename(filename)

        # Set up Jinja2 environment with custom delimiters and extensions.
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
            keep_trailing_newline=True,
        )

        # List to store post-processing functions.
        self.postprocessing_steps = []

        # Load user extensions and prepare them for the template environment.
        user_extensions = config["user_extensions"]
        extensions = Extension.get_extensions(user_extensions)
        for extension in extensions:
            config.setdefault(extension.__name__, {})
            ext_object = extension(config[extension.__name__])

            # Update template environment with extension methods and filters.
            self.jinja_env.globals.update(ext_object.methods)
            self.jinja_env.filters.update(ext_object.filters)

            # Add post-processing functions to the list.
            self.postprocessing_steps.extend(ext_object.post)

    def render(self):
        """
        Render the template.

        Returns:
            str: The rendered template output.

        This method renders the template, handles errors, and applies
        post-processing.
        """
        # Attempt to render the template.
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

        # Apply post-processing and return the output.
        output = self.postprocess(output)
        return output

    def postprocess(self, input_str):
        """
        Apply post-processing steps to the input string.

        Args:
            input_str (str): The input string to be post-processed.

        Returns:
            str: The post-processed output string.
        """
        for post_function in self.postprocessing_steps:
            input_str = post_function(input_str)
        return input_str

    @staticmethod
    def make_template(src_tree):
        """
        Generate a template string from a source tree.

        Args:
            src_tree (dict): A dictionary containing source sections.

        Returns:
            str: The generated template string.

        This static method generates a template string that includes the
        source sections.
        """
        lines = []
        for section, content in src_tree.items():
            if section != "prelude":
                # Add section headers.
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
                # Number the included files unless there is only one
                index_str = "" if len(content) == 1 else str(index)
                src_filename = f"{section}{index_str}.pss"
                # Include the current source file
                lines.append(f'(% include "{src_filename}" +%)')
        return "\n".join(lines).strip()

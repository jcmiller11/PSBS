"""
HTML BUILDER MODULE

This module provides a function to build an HTML game from PuzzleScript
source code. The function fetches the standalone inlined HTML template from
the provided PuzzleScript engine and replaces placeholders in the template
with the actual game data and options.

Example:
    filename = build_html("https://www.puzzlescript.net/", puzzle_script_code)
    print(f"HTML game generated: {filename}")

"""

from json import dumps
from os import path
from requests import get

from .errors import PSBSError
from .psparser import PSParser
from .utils import write_file, url_join


def build_html(engine, source):
    """
    Build an HTML game from PuzzleScript source code.

    This function fetches the standalone inlined HTML template from the
    provided PuzzleScript engine and then replaces placeholders in the
    template with the actual game data and options.

    Args:
        engine (str): The base URL of the PuzzleScript engine.
        source (str): The PuzzleScript source code.

    Returns:
        str: The filename of the generated HTML file.

    Raises:
        PSBSError: If any errors occur during the building process.
    """
    # Fetch the standalone inlined HTML template
    standalone_url = url_join(engine, "standalone_inlined.txt")
    response = get(standalone_url, timeout=5)
    if response.status_code != 200:
        err_message = []
        err_message.append("Error: Can't build html game")
        err_message.append(f"  Unable to download {standalone_url}")
        err_message.append(f"  Server response: {response.status_code}")
        raise PSBSError("\n".join(err_message))

    standalone_html = response.content.decode("UTF-8")
    parser = PSParser(source)
    prelude_options = parser.prelude_options

    # Placeholder replacements
    replacements = {
        "__GAMETITLE__": prelude_options.get("title", "My Game"),
        "__AUTHOR__": prelude_options.get("author", ""),
        "__HOMEPAGE__": prelude_options.get("homepage", engine),
        "__HOMEPAGE_STRIPPED_PROTOCOL__": prelude_options.get(
            "homepage", engine
        ).split("://", 1)[-1],
        "___BGCOLOR___": prelude_options.get("background_color", "black"),
        "___TEXTCOLOR___": prelude_options.get("text_color", "lightblue"),
        '"__GAMEDAT__"': dumps(source),
        "__GAMEDAT__": dumps(source),
    }

    # Replace placeholders with actual values
    for placeholder, value in replacements.items():
        standalone_html = standalone_html.replace(placeholder, value)

    # Write the generated HTML file
    filename = path.join(
        "bin", prelude_options.get("title", "My Game") + ".html"
    )
    write_file(filename, standalone_html)
    return filename

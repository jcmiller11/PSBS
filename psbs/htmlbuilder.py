from json import dumps
from os import path
from requests import get

from .psparser import PSParser
from .utils import write_file, url_join


def build_html(engine, source):
    standalone_url = url_join(engine, "standalone_inlined.txt")
    response = get(standalone_url, timeout=5)
    if response.status_code != 200:
        print("Error: Can't build html game")
        print(f"  Unable to download {standalone_url}")
        print(f"  Server response: {response.status_code}")
        raise SystemExit(1)
    standalone_html = response.content.decode("UTF-8")
    parser = PSParser(source)
    prelude_options = parser.prelude_options

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

    for placeholder, value in replacements.items():
        standalone_html = standalone_html.replace(placeholder, value)

    filename = path.join(
        "bin", prelude_options.get("title", "My Game") + ".html"
    )
    write_file(filename, standalone_html)
    return filename

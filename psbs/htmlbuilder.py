from json import dumps
from os import path
from requests import get

from .psparser import PSParser
from .utils import write_file


def build_html(engine, source):
    standalone_url = "/".join(engine.split("/") + ["standalone_inlined.txt"])
    response = get(standalone_url, timeout=5)
    if response.status_code != 200:
        print("Error: Can't build html game")
        print(f"  Unable to download {standalone_url}")
        print(f"  Server response: {response.status_code}")
        raise SystemExit(1)
    standalone_html = response.content.decode("UTF-8")
    parser = PSParser(source)
    title = parser.prelude_options.get("title", "My Game")
    homepage = parser.prelude_options.get("homepage", engine)
    if "://" in homepage:
        homepage_stripped_protocol = homepage.split("://", 1)[1]
    else:
        homepage_stripped_protocol = homepage
    standalone_html = standalone_html.replace(
        "__GAMETITLE__", parser.prelude_options.get("title", "My Game")
    )
    standalone_html = standalone_html.replace("__HOMEPAGE__", homepage)
    standalone_html = standalone_html.replace(
        "__HOMEPAGE_STRIPPED_PROTOCOL__", homepage_stripped_protocol
    )
    standalone_html = standalone_html.replace(
        "___BGCOLOR___",
        parser.prelude_options.get("background_color", "black"),
    )
    standalone_html = standalone_html.replace(
        "___TEXTCOLOR___",
        parser.prelude_options.get("text_color", "lightblue"),
    )
    # for some reason some older forks have extra quotes
    standalone_html = standalone_html.replace('"__GAMEDAT__"', dumps(source))
    standalone_html = standalone_html.replace("__GAMEDAT__", dumps(source))

    filename = path.join("bin", title + ".html")
    write_file(path.join("bin", title + ".html"), standalone_html)
    return filename

from os import path
from shutil import rmtree
from pathlib import PurePath
from asyncio import get_event_loop
from json import dumps

from pyppeteer import launch

from .config import Config
from .extension import Extension
from .htmlbuilder import build_html
from .gister import Gister
from .psparser import PSParser
from .template import Template
from .utils import (
    read_file,
    write_file,
    write_yaml,
    make_dir,
    run_in_browser,
    url_join,
)


class PSBSProject:
    def __init__(self, config_filename="config.yaml"):
        self.config = Config(config_filename)
        self.filename = None

    def build(self, verify=False):
        # Check for target directory
        if not path.exists("bin"):
            print("bin directory does not exist, creating one")
            make_dir("bin")

        readme_path = path.join("bin", "readme.txt")
        script_path = path.join("bin", "script.txt")

        # Build the readme.txt
        print(f"Writing file {readme_path}")
        write_file(
            readme_path,
            "Play this game by pasting the script in "
            + url_join(self.config["engine"], "editor.html"),
        )

        # Build the script.txt
        print("Building script.txt")
        source = Template(
            path.join("src", self.config["template"]), self.config
        ).render()

        print(f"Writing file {script_path}")
        write_file(script_path, source)
        if verify:
            self.print_ps_console(source)

    def export(self):
        if not self.config["gist_id"]:
            print("Writing game to html file")
            self.filename = build_html(
                self.config["engine"],
                read_file(path.join("bin", "script.txt")),
            )
        else:
            print("Updating gist")
            gist = Gister(gist_id=self.config["gist_id"])
            gist.write(path.join("bin", "readme.txt"))
            gist.write(path.join("bin", "script.txt"))

    def run(self, editor=False):
        print("Opening in browser")
        if self.filename:
            url = PurePath(path.abspath(self.filename)).as_uri()
        else:
            if editor:
                url = url_join(self.config["engine"], "editor.html?hack=")
            else:
                url = url_join(self.config["engine"], "play.html?p=")
            url += self.config["gist_id"]
        run_in_browser(url)

    def print_ps_console(self, source):
        async def run_in_psfork():
            try:
                browser = await launch()
            except OSError as err:
                print(f"Failed to launch headless Chromium instance\n  {err}")
                print("On Windows this may be caused by this issue:")
                print("https://github.com/pyppeteer/pyppeteer/issues/248")
                raise SystemExit(1) from err
            page = await browser.newPage()
            editor_url = url_join(self.config["engine"], "editor.html")
            await page.goto(editor_url)
            await page.evaluate("editor.setValue(" + dumps(source) + ")")
            await page.evaluate('compile(["restart"])')
            for message in await page.querySelectorAll(
                "div#consoletextarea div"
            ):
                message_text = await page.evaluate(
                    "(element) => element.textContent", message
                )
                if message_text == "=================================":
                    pass
                elif message_text.startswith("too many errors"):
                    print(message_text)
                    raise SystemExit(1)
                elif message_text.startswith("Rule Assembly"):
                    print(message_text.split("===========")[-1])
                else:
                    print(message_text)

        get_event_loop().run_until_complete(run_in_psfork())

    @staticmethod
    def create(project_name, gist_id=None, file=None, new_gist=False):
        source = ""
        engine = "https://www.puzzlescript.net/"

        if file:
            source = read_file(file)
        elif gist_id:
            print("Downloading data from gist")
            gist = Gister(gist_id=gist_id)
            source = gist.read("script.txt")
            engine = PSParser.get_engine(gist.read("readme.txt"))
        else:
            source = read_file(
                path.join(path.realpath(path.dirname(__file__)), "example.txt")
            )

        src_tree = PSParser(source).source_tree

        if new_gist:
            print("Creating new gist")
            gist = Gister()
            gist_id = gist.create(name=project_name)

        config_dict = {
            "gist_id": gist_id,
            "engine": engine,
            "template": "main.pss",
            "user_extensions": [],
        }
        config_dict.update(Extension.get_extension_configs())

        print("Building directory structure")
        make_dir(project_name)
        try:
            make_dir(path.join(project_name, "src"))
            make_dir(path.join(project_name, "bin"))

            print("Creating config file")
            write_yaml(path.join(project_name, "config.yaml"), config_dict)

            print("Creating template file")
            write_file(
                path.join(project_name, "src", "main.pss"),
                Template.make_template(src_tree),
            )

            print("Creating source files")
            for section_name, src_blocks in src_tree.items():
                for index, src_content in enumerate(src_blocks):
                    index += 1
                    if len(src_blocks) == 1:
                        index = ""
                    src_filename = f"{section_name}{index}.pss"
                    write_file(
                        path.join(project_name, "src", src_filename),
                        f"\n{src_content}\n",
                    )
        except SystemExit as err:
            print("Cleaning up!")
            rmtree(project_name)
            raise SystemExit(1) from err

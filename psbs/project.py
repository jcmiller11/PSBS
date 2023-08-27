"""
PSBSPROJECT MODULE

This module provides a class to represent a PuzzleScript project in PSBS.

Example:
    project = PSBSProject()
    project.build(verify=True)
    project.export()
    project.run(editor=False)

"""

from os import path
from shutil import rmtree
from pathlib import PurePath
from asyncio import get_event_loop
from json import dumps

from pyppeteer import launch

from .config import get_config
from .errors import PSBSError
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
    """
    A class representing a PuzzleScript project in PSBS.

    This class provides methods for building, exporting, running, and
    creating PuzzleScript projects. It integrates with various other modules
    to handle tasks such as generating templates, reading configuration,
    managing gists, and more.

    Args:
        config_filename (str, optional): The name of the configuration file.
            Defaults to 'config.yaml'.

    Attributes:
        config (dict): The project configuration.
        filename (str): The compiled HTML filename, if applicable.

    Methods:
        build(verify=False): Build the PuzzleScript game files in the 'bin'
            directory.
        export(): Export the PuzzleScript game to HTML or update a gist.
        run(editor=False): Run the PuzzleScript game in a web browser.
        print_ps_console(source): Print the PuzzleScript console output using
            a headless browser.
        create(project_name, gist_id=None, file=None, new_gist=False): Create
            a PSBS project directory and populate it with necessary files.
    """

    def __init__(self, config_filename="config.yaml"):
        self.config = get_config(config_file=config_filename)
        self.filename = None

    def build(self, verify=False):
        """
        Build the PuzzleScript game files in the 'bin' directory.

        This method creates or updates the 'readme.txt' and 'script.txt'
        files in the 'bin' directory. The 'readme.txt' file contains a
        message about playing the game using the PuzzleScript editor. The
        'script.txt' file is generated from the template specified in the
        configuration.

        Args:
            verify (bool, optional): If True, verify the built game using the
                print_ps_console method. Defaults to False.
        """
        # Check for target directory
        if not path.exists("bin"):
            print("bin directory does not exist, creating one")
            make_dir("bin")

        readme_path = path.join("bin", "readme.txt")
        script_path = path.join("bin", "script.txt")

        # Build the readme.txt
        editor_url = url_join(self.config["engine"], "editor.html")
        print(f"Writing file {readme_path}")
        write_file(
            readme_path,
            f"Play this game by pasting the script in {editor_url}",
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
        """
        Export the PuzzleScript game to HTML or update a gist.

        If the project doesn't have a gist, compiles game to an HTML file.
        If the project has a gist it updates the 'readme.txt' and 'script.txt'
        files on the gist.
        """
        if not self.config["gist_id"]:
            # If project doesn't have a gist, create an HTML file
            print("Writing game to html file")
            self.filename = build_html(
                self.config["engine"],
                read_file(path.join("bin", "script.txt")),
            )
        else:
            # If project has a gist, update the gist files
            print("Updating gist")
            gist = Gister(gist_id=self.config["gist_id"])
            gist.write(path.join("bin", "readme.txt"))
            gist.write(path.join("bin", "script.txt"))

    def run(self, editor=False):
        """
        Run the PuzzleScript game in a web browser.

        Args:
            editor (bool, optional): If True, open the PuzzleScript editor.
                If False, open the play mode. Defaults to False.
        """
        print("Opening in browser")
        if self.filename:
            # Run from file if compiled to HTML
            url = PurePath(path.abspath(self.filename)).as_uri()
        else:
            # Otherwise run from web
            if editor:
                url = url_join(self.config["engine"], "editor.html?hack=")
            else:
                url = url_join(self.config["engine"], "play.html?p=")
            url += self.config["gist_id"]
        run_in_browser(url)

    def print_ps_console(self, source):
        """
        Print the PuzzleScript console output using a headless browser.

        Args:
            source (str): The PuzzleScript source code to be evaluated.

        Raises:
            PSBSError: If an error occurs during the console output retrieval.
        """

        async def run_in_psfork():
            try:
                # Attempt to launch headless browser
                browser = await launch()
            except OSError as err:
                err_message = [
                    f"Failed to launch headless Chromium instance\n  {err}",
                    "On Windows this may be caused by this issue:",
                    "https://github.com/pyppeteer/pyppeteer/issues/248",
                ]
                raise PSBSError("\n".join(err_message)) from err

            # Load editor.html from PuzzleScript engine
            page = await browser.newPage()
            editor_url = url_join(self.config["engine"], "editor.html")
            await page.goto(editor_url)

            # Insert source and compile
            await page.evaluate("editor.setValue(" + dumps(source) + ")")
            await page.evaluate('compile(["restart"])')

            # Retrieve and format compilation messages
            for message in await page.querySelectorAll(
                "div#consoletextarea div"
            ):
                message_text = await page.evaluate(
                    "(element) => element.textContent", message
                )
                if message_text.startswith("too many errors"):
                    raise PSBSError(message_text)
                if message_text.startswith("Rule Assembly"):
                    print(message_text.split("===========")[-1])
                elif message_text != "=================================":
                    print(message_text)

        # Run async function
        get_event_loop().run_until_complete(run_in_psfork())

    @staticmethod
    def create(project_name, gist_id=None, file=None, new_gist=False):
        """
        Create a PSBS project directory and populate it with necessary files.

        Args:
            project_name (str): Name of the project directory.
            gist_id (str, optional): Gist ID if using an existing gist.
            file (str, optional): Path to the input file.
            new_gist (bool, optional): Create a new gist for the project.

        Raises:
            PSBSError: If any errors occur during project creation.
        """
        source = ""
        engine = "https://www.puzzlescript.net/"

        # Determine the source of the PuzzleScript code
        if file:
            source = read_file(file)
        elif gist_id:
            print("Downloading data from gist")
            gist = Gister(gist_id=gist_id)
            source = gist.read("script.txt")
            engine = PSParser.get_engine(gist.read("readme.txt"))
        else:
            # If no file or gist is provided, use an example source
            source = read_file(
                path.join(path.realpath(path.dirname(__file__)), "example.txt")
            )

        # Parse the source into sections
        src_tree = PSParser(source).source_tree

        # Create a new gist if requested
        if new_gist:
            print("Creating new gist")
            gist = Gister()
            gist_id = gist.create(name=project_name)

        # Get config and set values for the project
        config_dict = get_config()
        config_dict["gist_id"] = gist_id or ""
        config_dict["engine"] = engine

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
        except PSBSError as err:
            print("Cleaning up!")
            rmtree(project_name)
            raise err

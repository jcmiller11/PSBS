from os import path
from shutil import rmtree

from .gister import Gister
from .config import Config
from .psparser import split_ps, get_engine
from .templatebuilder import make_template
from .utils import read_file, write_file, write_yaml, make_dir, run_in_browser
from .template import render_template


class PSBSProject:
    def __init__(self, config_filename="config.yaml"):
        self.config = Config(config_filename)

    def build(self):
        # Check for target directory
        if not path.exists("bin"):
            print("bin directory does not exist, creating one")
            make_dir("bin")

        # Build the readme.txt
        print("Writing file bin/readme.txt")
        write_file("bin/readme.txt",
                   "Play this game by pasting the script in "
                   f"{self.config['engine']}editor.html")

        # Build the script.txt
        print("Building script.txt")
        source = render_template(f"src/{self.config['template']}")

        print("Writing file bin/script.txt")
        write_file("bin/script.txt", source)

    def upload(self):
        gist_id = self.config['gist_id']
        if not self.config['gist_id']:
            print("Error: Unable to upload without a gist_id in config file")
            raise SystemExit(1)

        print("Updating gist")
        gist = Gister(gist_id)
        gist.write("bin/readme.txt")
        gist.write("bin/script.txt")

    def run(self, editor=False):
        print("Opening in browser")
        if editor:
            url_string = "editor.html?hack="
        else:
            url_string = "play.html?p="
        run_in_browser(self.config['engine']+url_string+self.config['gist_id'])

    @staticmethod
    def create(project_name, gist_id=None, file=None):
        src_directory = f"{project_name}/src/"
        bin_directory = f"{project_name}/bin/"

        source = ""
        engine = "https://www.puzzlescript.net/"

        if gist_id:
            print("Downloading data from gist")
            gist = Gister(gist_id)
            source = gist.read("script.txt")
            engine = get_engine(gist.read("readme.txt"))

        if file:
            source = read_file(file)

        src_tree = split_ps(source)

        print("Building directory structure")
        make_dir(project_name)
        try:
            make_dir(src_directory)
            make_dir(bin_directory)
    
            print("Creating config file")
            write_yaml(f"{project_name}/config.yaml", {
                'gist_id': gist_id,
                'engine': engine,
                'template': "main.pss"})
    
            print("Creating template file")
            write_file(f"{src_directory}/main.pss", make_template(src_tree))
    
            print("Creating source files")
            for section_name, src_blocks in src_tree.items():
                for index, src_content in enumerate(src_blocks):
                    index += 1
                    if len(src_blocks) == 1:
                        index = ""
                    src_filename = f"{section_name}{index}.pss"
                    write_file(src_directory+src_filename, src_content)
        except SystemExit as err:
            print("Cleaning up!")
            rmtree(project_name)
            raise SystemExit(1) from err


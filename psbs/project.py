#!/usr/bin/env python3

import webbrowser
import traceback
from os import path, mkdir

import yaml
import jinja2
from .gister import Gister


class PSBSProject:
    def __init__(self, config_filename="config.yaml"):
        try:
            with open(config_filename, "rb") as config_file:
                self.config = yaml.safe_load(config_file)
            if isinstance(self.config, str):
                raise yaml.YAMLError("YAML syntax malformed")
        except IOError as err:
            print(f"Error: Config file not found\n  {err}")
            raise SystemExit(1) from err
        except yaml.YAMLError as err:
            print(f"Error: Problem parsing config file\n  {err}")
            raise SystemExit(1) from err

    def build(self):
        # Check for target directory
        if not path.exists("bin"):
            print("bin directory does not exist, creating one")
            try:
                mkdir("bin")
            except (OSError, PermissionError) as err:
                print(f"Error: Unable to create bin directory\n  {err}")
                raise SystemExit(1) from err

        # Build the readme.txt
        print("Writing file bin/readme.txt")
        try:
            with open("bin/readme.txt", "w", encoding='UTF-8') as readme_file:
                readme_file.write("Play this game by pasting the script in ")
                readme_file.write(f"{self.config['engine']}editor.html")
        except IOError as err:
            print(f"Error: Unable to write file readme.txt\n  {err}")
            raise SystemExit(1) from err
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err

        # Build the script.txt
        print("Building script.txt")
        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("src"),
            autoescape=False
        )
        try:
            template = jinja_env.get_template(self.config['template'])
            source = template.render()
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err
        except jinja2.exceptions.TemplateNotFound as err:
            print(f"Error: Unable to find template '{err}'")
            raise SystemExit(1) from err
        except jinja2.exceptions.TemplateError as err:
            print(f"Error: Unable to render template\n  {err}")
            print(traceback.format_exc().split('\n')[-4])
            raise SystemExit(1) from err

        print("Writing file bin/script.txt")
        try:
            with open("bin/script.txt", "w", encoding='UTF-8') as readme_file:
                readme_file.write(source)
        except IOError as err:
            print(f"Error: Unable to write file script.txt\n  {err}")
            raise SystemExit(1) from err

    def upload(self):
        try:
            gist_id = self.config['gist_id']
        except KeyError as err:
            print("Error: Unable to upload without a gist_id in config file")
            raise SystemExit(1) from err
        if not self.config['gist_id']:
            print("Error: Unable to upload without a gist_id in config file")
            raise SystemExit(1)

        print("Updating gist")
        gist = Gister(gist_id)
        gist.write("bin/readme.txt")
        gist.write("bin/script.txt")

    def run(self):
        print("Opening in browser")
        try:
            webbrowser.open(
                f"{self.config['engine']}play.html?p={self.config['gist_id']}",
                new=2)
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err
        except webbrowser.Error as err:
            print("Error: Unable to find user preferred browser to launch")
            raise SystemExit(1) from err

    @staticmethod
    def create(project_name):
        # TODO: add functionality for "new project from gist"
        # Ideally we'd pull the puzzlescript source from the gist
        # and split it into src files
        # define project defaults
        psbs_path = path.realpath(path.dirname(__file__))
        default_config = {
            'gist_id': "",
            'engine': "https://www.puzzlescript.net/",
            'template': "main.pss"}
        standard_src_files = [
            'prelude.pss',
            'objects.pss',
            'legend.pss',
            'sounds.pss',
            'collisionlayers.pss',
            'rules.pss',
            'winconditions.pss',
            'levels.pss'
        ]
        src_directory = f"{project_name}/src/"
        bin_directory = f"{project_name}/bin/"

        print("Building directory structure")
        try:
            mkdir(project_name)
        except (OSError, PermissionError) as err:
            print(f"Error: Unable to create project directory\n  {err}")
            raise SystemExit(1) from err
        try:
            mkdir(src_directory)
        except (OSError, PermissionError) as err:
            print(f"Error: Unable to create source directory\n  {err}")
            raise SystemExit(1) from err
        try:
            mkdir(bin_directory)
        except (OSError, PermissionError) as err:
            print(f"Error: Unable to create bin directory\n  {err}")
            raise SystemExit(1) from err

        print("Creating config file")
        try:
            with open(f"{project_name}/config.yaml", "w", encoding='UTF-8') as config_file:
                yaml.dump(default_config, config_file)
        except IOError as err:
            print(f"Error: Unable to write config file\n  {err}")
            raise SystemExit(1) from err

        print("Creating default template file")
        try:
            with open(f"{psbs_path}/main.pss", "r", encoding='UTF-8') as template_file:
                default_template = template_file.read()
        except IOError as err:
            print(f"Error: Unable to read default template in installation directory\n  {err}")
            raise SystemExit(1) from err
        try:
            with open(f"{src_directory}/main.pss", "w", encoding='UTF-8') as template_file:
                template_file.write(default_template)
        except IOError as err:
            print(f"Warning: Unable to write file {src_directory}main.pss\n  {err}")

        print("Creating source files")
        for src_filename in standard_src_files:
            try:
                with open(src_directory+src_filename, "w", encoding='UTF-8') as _:
                    pass
            except IOError as err:
                print(f"Warning: Unable to write file {src_directory}{src_filename}\n  {err}")

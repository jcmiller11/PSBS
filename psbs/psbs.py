#!/usr/bin/env python3

import tomllib
import webbrowser
import subprocess
from sys import argv
from os import environ, getenv, path, mkdir
from inspect import cleandoc
from gistyc import GISTyc

def get_token():
    if "PSBS_GH_TOKEN" in environ:
        return getenv('PSBS_GH_TOKEN')
    try:
        return subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()
    except FileNotFoundError as err:
        print("ERROR: gh-cli does not appear to be installed, aborting upload")
        raise SystemExit(1) from err
    except subprocess.CalledProcessError as err:
        print("ERROR: gh-cli refuses to provide token, aborting upload")
        raise SystemExit(1) from err

class PSBSProject:
    def __init__(self, config_filename = "config.toml"):
        print(config_filename)
        try:
            with open(config_filename, "rb") as config_file:
                self.config = tomllib.load(config_file)
        except IOError as err:
            print(f"Error: Config file not found\n  {err}")
            raise SystemExit(1) from err

    class GistError(Exception):
        '''Thrown when GitHub refuses to create or update the gist'''

    def build(self):
        # Build the readme.txt
        if not path.exists("bin"):
            print("bin directory does not exist, creating one")
            try:
                mkdir("bin")
            except (OSError, PermissionError) as err:
                print(f"Error: Unable to create bin directory\n  {err}")
                raise SystemExit(1) from err
            print ("Writing file bin/readme.txt")
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
        print ("Building script.txt")
        layout = {
            "prelude":"",
            "objects":"",
            "legend":"",
            "sounds":"",
            "collisionlayers":"",
            "rules":"",
            "winconditions":"",
            "levels":""
        }

        for key in layout:
            try:
                for src_filename in self.config[key]:
                    print(f" Importing file src/{src_filename}")
                    try:
                        with open(f"src/{src_filename}", "r", encoding='UTF-8') as src_file:
                            layout[key] += f"{src_file.read()}\n\n"
                    except IOError as err:
                        print(f"Warning: Unable to read file {src_filename}\n  {err}")
            except KeyError as err:
                print(f"Warning: Unable to find {err} directive in config file")

        def make_section(name,has_title = True):
            if has_title:
                return f"========\n{name.upper()}\n========\n\n{layout[name]}"
            return layout[name]

        source = make_section("prelude", False)
        source += make_section("objects")
        source += make_section("legend")
        source += make_section("sounds")
        source += make_section("collisionlayers")
        source += make_section("rules")
        source += make_section("winconditions")
        source += make_section("levels")

        print ("Writing file bin/script.txt")
        try:
            with open("bin/script.txt", "w", encoding='UTF-8') as readme_file:
                readme_file.write(source)
        except IOError as err:
            print(f"Error: Unable to write file script.txt\n  {err}")
            raise SystemExit(1) from err

    def upload(self):
        print("Updating gist")
        try:
            gist_id = self.config['gist_id']
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err

        token = get_token()
        try:
            gist_api = GISTyc(auth_token=token)
            response_update_data = gist_api.update_gist(file_name="bin/readme.txt",gist_id=gist_id)
            if "message" in response_update_data:
                raise self.GistError(response_update_data['message'])
            response_update_data = gist_api.update_gist(file_name="bin/script.txt",gist_id=gist_id)
            if "message" in response_update_data:
                raise self.GistError(response_update_data['message'])
        except ConnectionError as err:
            print("Error: Unable to connect to GitHub, aborting upload")
            raise SystemExit(1) from err
        except self.GistError as err:
            print(f"Error: Unable to update gist\n  Response: {err}")
            raise SystemExit(1) from err

    def run(self):
        print("Opening in browser")
        try:
            webbrowser.open(f"{self.config['engine']}play.html?p={self.config['gist_id']}", new=2)
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err
        except webbrowser.Error as err:
            print("Error: Unable to find user preferred browser to launch")
            raise SystemExit(1) from err

def new(project_name):
    #TODO: add functionality for "new project from gist"
    #Ideally we'd pull the puzzlscript source from the gist and split it into src files
    print("Building directory structure")
    try:
        mkdir(project_name)
    except (OSError, PermissionError) as err:
        print(f"Error: Unable to create project directory\n  {err}")
        raise SystemExit(1) from err
    try:
        mkdir(f"{project_name}/src")
    except (OSError, PermissionError) as err:
        print(f"Error: Unable to create source directory\n  {err}")
        raise SystemExit(1) from err
    try:
        mkdir(f"{project_name}/bin")
    except (OSError, PermissionError) as err:
        print(f"Error: Unable to create bin directory\n  {err}")
        raise SystemExit(1) from err

    config_text = '''gist_id = ""

    engine = "https://www.puzzlescript.net/"

    prelude = ["prelude.pss"]
    objects = ["objects.pss"]
    legend = ["legend.pss"]
    sounds = ["sounds.pss"]
    collisionlayers = ["collisionlayers.pss"]
    rules = ["rules.pss"]
    winconditions = ["winconditions.pss"]
    levels = ["levels.pss"]
    '''
    print("Creating config file")
    try:
        with open(f"{project_name}/config.toml", "w", encoding='UTF-8') as config_file:
            config_file.write(cleandoc(config_text))
    except IOError as err:
        print(f"Error: Unable to write config file\n  {err}")
        raise SystemExit(1) from err
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
    for src_filename in standard_src_files:
        try:
            with open(f"{project_name}/src/{src_filename}", "w", encoding='UTF-8') as src_file:
                pass
        except IOError as err:
            print(f"Warning: Unable to write file {project_name}/src/{src_filename}\n  {err}")

def show_commands():
    print("\033[1mCOMMANDS\033[0m")
    print("build:\tBuild project")
    print("upload:\tBuild project then upload to gist")
    print("run:\tBuild project, upload to gist, then launch in browser")
    print("new:\tCreate a new project")

def main():
    #TODO: refactor with argparse or similar
    if len(argv)>1:
        first_arg = argv[1].lower()
        if first_arg == "build":
            project = PSBSProject()
            project.build()
        elif first_arg == "upload":
            project = PSBSProject()
            project.build()
            project.upload()
        elif first_arg == "run":
            project = PSBSProject()
            project.build()
            project.upload()
            project.run()
        elif first_arg == "new":
            if len(argv<3):
                print("Please provide a name for the new project")
            else:
                new(argv[2])
        else:
            print("I didn't understand that\n")
            show_commands()
    else:
        print("PSBS - PuzzleScript Build System\n")
        show_commands()

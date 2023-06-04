#!/usr/bin/env python3

import tomllib
import webbrowser
import subprocess
import traceback
from sys import argv
from os import environ, getenv, path, mkdir
from inspect import cleandoc

import jinja2
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

        print ("Writing file bin/script.txt")
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

    config_text = 'gist_id = ""\nengine = "https://www.puzzlescript.net/"\ntemplate = "main.pss"'

    print("Creating config file")
    try:
        with open(f"{project_name}/config.toml", "w", encoding='UTF-8') as config_file:
            config_file.write(cleandoc(config_text))
    except IOError as err:
        print(f"Error: Unable to write config file\n  {err}")
        raise SystemExit(1) from err

    print("Creating default template file")
    psbs_path = path.realpath(path.dirname(__file__))
    try:
        with open(f"{psbs_path}/main.pss", "r", encoding='UTF-8') as template_file:
            default_template = template_file.read()
    except IOError as err:
        print(f"Error: Unable to read default template in installation directory\n  {err}")
        raise SystemExit(1) from err

    try:
        with open(f"{project_name}/src/main.pss", "w", encoding='UTF-8') as template_file:
            template_file.write(default_template)
    except IOError as err:
        print(f"Warning: Unable to write file {project_name}/src/main.pss\n  {err}")

    print("Creating source files")
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
            with open(f"{project_name}/src/{src_filename}", "w", encoding='UTF-8') as _:
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
            if len(argv)<3:
                print("Please provide a name for the new project")
            else:
                new(argv[2])
        else:
            print("I didn't understand that\n")
            show_commands()
    else:
        print("PSBS - PuzzleScript Build System\n")
        show_commands()

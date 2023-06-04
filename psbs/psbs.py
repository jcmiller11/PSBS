#!/usr/bin/env python3

import tomllib
import webbrowser
import subprocess
from sys import argv
from os import environ, getenv
from gistyc import GISTyc

def load_config():
    global config
    #FIXME: refactor as psbs project class to remove global
    try:
        with open("config.toml", "rb") as config_file:
            config = tomllib.load(config_file)
    except IOError as err:
        print(f"Error: Config file not found\n  {err}")
        raise SystemExit(1) from err

class GistError(Exception):
    """Thrown when GitHub refuses to create or update the gist"""

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

def build():
    # Build the readme.txt
    print ("Writing file bin/readme.txt")
    try:
        with open("bin/readme.txt", "w", encoding='UTF-8') as readme_file:
            readme_file.write("Play this game by pasting the script in ")
            readme_file.write(f"{config['engine']}editor.html")
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
            for src_filename in config[key]:
                print(f" Importing file src/{src_filename}")
                try:
                    with open(f"src/{src_filename}", "r", encoding='UTF-8') as src_file:
                        layout[key] += f"{src_file.read()}\n\n"
                except IOError as err:
                    print(f"Warning: Unable to read file {src_filename}\n  {err}")
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err

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

def upload():
    print("Updating gist")
    try:
        gist_id = config['gist_id']
    except KeyError as err:
        print(f"Error: Unable to find {err} directive in config file")
        raise SystemExit(1) from err

    token = get_token()
    try:
        gist_api = GISTyc(auth_token=token)
        response_update_data = gist_api.update_gist(file_name="bin/readme.txt",gist_id=gist_id)
        if "message" in response_update_data:
            raise GistError(response_update_data['message'])
        response_update_data = gist_api.update_gist(file_name="bin/script.txt",gist_id=gist_id)
        if "message" in response_update_data:
            raise GistError(response_update_data['message'])
    except ConnectionError as err:
        print("Error: Unable to connect to GitHub, aborting upload")
        raise SystemExit(1) from err
    except GistError as err:
        print(f"Error: Unable to update gist\n  Response: {err}")
        raise SystemExit(1) from err

def run():
    print("Opening in browser")
    try:
        webbrowser.open(f"{config['engine']}play.html?p={config['gist_id']}", new=2)
    except KeyError as err:
        print(f"Error: Unable to find {err} directive in config file")
        raise SystemExit(1) from err
    except webbrowser.Error as err:
        print("Error: Unable to find user preferred browser to launch")
        raise SystemExit(1) from err

def new():
    print("make a new project")
    #TODO: add this functionality

def show_commands():
    print("PSBS - PuzzleScript Build System\n")
    print("\033[1mCOMMANDS\033[0m")
    print("help:\tDisplay help dialog")
    print("build:\tBuild project")
    print("upload:\tBuild project then upload to gist")
    print("run:\tBuild project, upload to gist, then launch in browser")

def show_help():
    show_commands()
    #TODO: add explanation of how to connect your github auth token

def main():
    if len(argv)>1:
        first_arg = argv[1].lower()
        if first_arg == "build":
            load_config()
            build()
        elif first_arg == "upload":
            load_config()
            build()
            upload()
        elif first_arg == "run":
            load_config()
            build()
            upload()
            run()
        elif first_arg == "new":
            new()
        elif first_arg == "help":
            show_help()
    else:
        show_commands()

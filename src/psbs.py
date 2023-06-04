#!/usr/bin/env python3

import tomllib
import webbrowser
import subprocess
from sys import argv
from gistyc import GISTyc
from os import environ, getenv
from requests.exceptions import ConnectionError

try:
	with open("config.toml", "rb") as config_file:
		config = tomllib.load(config_file)
except IOError as e:
	print(f"Error: Unable to read config file\n\t{e}")
	raise SystemExit(1)

class GistError(Exception):
	"""Thrown when GitHub refuses to create or update the gist"""
	pass

def get_token():
	if "PSBS_GH_TOKENs" in environ:
		return getenv('PSBS_GH_TOKEN')
	else:
		try:
			return subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()
		except FileNotFoundError:
			print("ERROR: no PSBS_GH_TOKEN and fallback gh-cli does not appear to be installed, aborting upload")
			raise SystemExit(1)
		except subprocess.CalledProcessError:
			print("ERROR: no PSBS_GH_TOKEN and fallback gh-cli refuses to provide token, aborting upload")
			raise SystemExit(1)

def build():
	# Build the readme.txt
	print ("Writing file bin/readme.txt")
	try:
		with open("bin/readme.txt", "w") as readme_file:
			readme_file.write(f"Play this game by pasting the script in {config['engine']}editor.html")
	except IOError as e:
		print(f"Error: Unable to write file readme.txt\n\t{e}")
		raise SystemExit(1)
	except KeyError as e:
		print(f"Error: Unable to find {e} directive in config file")
		raise SystemExit(1)
	
	# Build the script.txt
	print ("Building file bin/script.txt")
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
					with open(f"src/{src_filename}", "r") as src_file:
						layout[key] += f"{src_file.read()}\n\n"
				except IOError as e:
					print(f"Warning: Unable to read file {src_filename}\n\t{e}")
		except KeyError as e:
			print(f"Error: Unable to find {e} directive in config file")
			raise SystemExit(1)
	
	def make_section(name,has_title = True):
		if has_title:
			return f"========\n{name.upper()}\n========\n\n{layout[name]}"
		else:
			return layout[name]
	
	source = make_section("prelude", False)
	source += make_section("objects")
	source += make_section("legend")
	source += make_section("sounds")
	source += make_section("collisionlayers")
	source += make_section("rules")
	source += make_section("winconditions")
	source += make_section("levels")
	
	try:
		with open("bin/script.txt", "w") as readme_file:
			readme_file.write(source)
	except IOError as e:
		print(f"Error: Unable to write file script.txt\n\t{e}")
		raise SystemExit(1)

def upload():
	print("Updating gist")
	try:
		gist_id = config['gist_id']
	except KeyError as e:
		print(f"Error: Unable to find {e} directive in config file")
		raise SystemExit(1)

	token = get_token()
	try:
		gist_api = GISTyc(auth_token=token)
		response_update_data = gist_api.update_gist(file_name="bin/readme.txt",gist_id=gist_id)
		if "message" in response_update_data:
			raise GistError(response_update_data['message'])
		response_update_data = gist_api.update_gist(file_name="bin/script.txt",gist_id=gist_id)
		if "message" in response_update_data:
			raise GistError(response_update_data['message'])
	except ConnectionError as e:
		print("Error: Unable to connect to GitHub, aborting upload")
		raise SystemExit(1)
	except GistError as e:
		print(f"Error: Unable to update gist\n\tResponse: {e}")
		raise SystemExit(1)

def run():
	print("Opening in browser")
	try:
		webbrowser.open(f"{config['engine']}play.html?p={config['gist_id']}", new=2)
	except KeyError as e:
		print(f"Error: Unable to find {e} directive in config file")
		raise SystemExit(1)
	except webbrowser.Error:
		print(f"Error: Unable to find user preferred browser to launch")
		raise SystemExit(1)

def new():
	print("make a new project")
	#TODO: add this functionality

def show_commands():
	print("PSBS - PuzzleScript Build System\n")
	print("\033[1mCOMMANDS\033[0m")
	print("help:\t Display help dialog")
	print("build:\tBuild project")
	print("upload:\tBuild project then upload to gist")
	print("run:\tBuild project, upload to gist, then launch in browser")

def help():
	show_commands()
	#TODO: add explanation of how to connect your github auth token

if len(argv)>1:
	first_arg = argv[1].lower()
	if first_arg == "build":
		build()
	elif first_arg == "upload":
		build()
		upload()
	elif first_arg == "run":
		build()
		upload()
		run()
	elif first_arg == "new":
		new()
	elif first_arg == "help":
		help()
else:
	show_commands()
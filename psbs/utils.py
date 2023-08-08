import webbrowser
from os import mkdir
from asyncio import get_event_loop
from json import dumps

from pyppeteer import launch
import yaml


def read_file(filename):
    try:
        with open(filename, "r", encoding="UTF-8") as file:
            return file.read()
    except IOError as err:
        print(f"Error: Unable to read input file\n  {err}")
        raise SystemExit(1) from err
    except UnicodeDecodeError as err:
        print(
            "Error: Unable to read input file, "
            "are you sure this is a text file?"
        )
        raise SystemExit(1) from err


def write_file(filename, data):
    try:
        with open(filename, "w", encoding="UTF-8") as file:
            file.write(data)
    except IOError as err:
        print(f"Error: Unable to write file {filename}\n  {err}")
        raise SystemExit(1) from err


def read_yaml(filename):
    try:
        with open(filename, "rb") as file:
            output = yaml.safe_load(file)
        if isinstance(output, str):
            raise yaml.YAMLError("YAML syntax malformed")
    except IOError as err:
        print(f"Error: Config file not found\n  {err}")
        raise SystemExit(1) from err
    except yaml.YAMLError as err:
        print(f"Error: Problem parsing config file\n  {err}")
        raise SystemExit(1) from err
    return output


def write_yaml(filename, data):
    try:
        with open(filename, "w", encoding="UTF-8") as file:
            yaml.safe_dump(data, file, sort_keys=False)
    except IOError as err:
        print(f"Error: Unable to write file {filename}\n  {err}")
        raise SystemExit(1) from err


def make_dir(filename):
    try:
        mkdir(filename)
    except (OSError, PermissionError) as err:
        print(f"Error: Unable to create directory {filename}\n  {err}")
        raise SystemExit(1) from err


def run_in_browser(url):
    try:
        webbrowser.open(url)
    except webbrowser.Error as err:
        print("Error: Unable to launch browser")
        raise SystemExit(1) from err

def print_ps_console(source):
    async def run_in_psfork():
        browser = await launch()
        page = await browser.newPage()
        await page.goto('https://www.puzzlescript.net/editor.html')
        await page.evaluate('editor.setValue('+dumps(source)+')')
        await page.evaluate('compile(["restart"])')
        for message in await page.querySelectorAll("div#consoletextarea div"):
            message_text = await page.evaluate('(element) => element.textContent', message)
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

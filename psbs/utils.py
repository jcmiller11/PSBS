"""
UTILITIES MODULE

This module provides various utility functions for file handling, YAML
parsing, directory creation, web browsing, and URL manipulation.
"""

import webbrowser
from os import mkdir

import yaml


def read_file(filename):
    """
    Read the content of a text file.

    Args:
        filename (str): The path to the file to be read.

    Returns:
        str: The content of the file.

    Raises:
        SystemExit: If there is an error reading the file.
    """
    try:
        with open(filename, "r", encoding="UTF-8") as file:
            return file.read()
    except IOError as err:
        print(f"Error: Unable to read input file\n  {err}")
        raise SystemExit(1) from err
    except UnicodeDecodeError as err:
        print("Error: Unable to read input file, is this a text file?")
        raise SystemExit(1) from err


def write_file(filename, data):
    """
    Write data to a text file.

    Args:
        filename (str): The path to the file to be written.
        data (str): The data to be written to the file.

    Raises:
        SystemExit: If there is an error writing the file.
    """
    try:
        with open(filename, "w", encoding="UTF-8") as file:
            file.write(data)
    except IOError as err:
        print(f"Error: Unable to write file {filename}\n  {err}")
        raise SystemExit(1) from err


def read_yaml(filename):
    """
    Read data from a YAML file.

    Args:
        filename (str): The path to the YAML file to be read.

    Returns:
        dict: The parsed data from the YAML file.

    Raises:
        SystemExit: If there is an error reading the file or parsing YAML.
    """
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
    """
    Write data to a YAML file.

    Args:
        filename (str): The path to the YAML file to be written.
        data (dict): The data to be written to the YAML file.

    Raises:
        SystemExit: If there is an error writing the file.
    """
    try:
        with open(filename, "w", encoding="UTF-8") as file:
            yaml.safe_dump(data, file, sort_keys=False)
    except IOError as err:
        print(f"Error: Unable to write file {filename}\n  {err}")
        raise SystemExit(1) from err


def make_dir(directory):
    """
    Create a directory.

    Args:
        directory (str): The path to the directory to be created.

    Raises:
        SystemExit: If there is an error creating the directory.
    """
    try:
        mkdir(directory)
    except (OSError, PermissionError) as err:
        print(f"Error: Unable to create directory {directory}\n  {err}")
        raise SystemExit(1) from err


def run_in_browser(url):
    """
    Open a URL in the default web browser.

    Args:
        url (str): The URL to be opened.

    Raises:
        SystemExit: If there is an error opening the URL.
    """
    try:
        webbrowser.open(url)
    except webbrowser.Error as err:
        print("Error: Unable to launch browser")
        raise SystemExit(1) from err


def url_join(*url_strings):
    """
    Join URL parts into a complete URL.

    Args:
        *url_strings (str): Multiple URL parts to be joined.

    Returns:
        str: The complete URL.
    """
    output_list = []
    for part in url_strings:
        output_list.extend(part.rstrip("/").split("/"))
    return "/".join(output_list)

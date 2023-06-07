from os import mkdir

import yaml


def write_file(filename, data):
    try:
        with open(filename, "w", encoding='UTF-8') as file:
            file.write(data)
    except IOError as err:
        print(f"Error: Unable to write file {filename}\n  {err}")
        raise SystemExit(1) from err


def write_yaml(filename, data):
    try:
        with open(filename, "w", encoding='UTF-8') as file:
            yaml.dump(data, file)
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


def make_dir(filename):
    try:
        mkdir(filename)
    except (OSError, PermissionError) as err:
        print(f"Error: Unable to create directory {filename}\n  {err}")
        raise SystemExit(1) from err

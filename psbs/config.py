from .utils import read_yaml


class Config(dict):
    def __init__(self, config_filename):
        super().__init__(read_yaml(config_filename))

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err

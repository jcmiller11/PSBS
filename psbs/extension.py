from os.path import join, dirname, basename, isfile
import glob
from importlib import import_module


class Extension:
    def __init__(self, config):
        self.methods = {}
        self.config = config
        if self.get_config():
            for key, value in self.get_config().items():
                if key not in self.config:
                    self.config[key] = None
                if not self.config[key]:
                    self.config[key] = value

    def register(self, name, function):
        if name not in self.methods:
            self.methods[name] = function

    @staticmethod
    def get_config():
        return None

    @classmethod
    def get_extensions(cls):
        for extension in glob.glob(join(dirname(__file__), "extensions", "*.py")):
            if isfile(extension) and not extension.endswith("__init__.py"):
                import_module(f"psbs.extensions.{basename(extension)[:-3]}")
        return cls.__subclasses__()

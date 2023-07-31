from os.path import join, dirname, basename, isfile
import glob
from importlib import import_module
from jinja2.exceptions import TemplateError


class Extension:
    def __init__(self, config):
        self.methods = {}
        self.post = []
        self.config = config
        for key, value in self.get_config().items():
            if key not in self.config:
                self.config[key] = None
            if self.config[key] is None:
                self.config[key] = value

    def register(self, name, function):
        if name not in self.methods:
            self.methods[name] = function

    def register_post(self, function):
        self.post.append(function)

    @staticmethod
    def get_config():
        return {}

    @classmethod
    def get_extensions(cls):
        for extension in glob.glob(
            join(dirname(__file__), "extensions", "*.py")
        ):
            if isfile(extension) and not extension.endswith("__init__.py"):
                import_module(f"psbs.extensions.{basename(extension)[:-3]}")
        return cls.__subclasses__()

    @classmethod
    def get_extension_configs(cls):
        config_dict = {}
        for extension in cls.get_extensions():
            if extension.get_config():
                config_dict[extension.__name__] = extension.get_config()
        return config_dict

    class ExtensionError(TemplateError):
        """Thrown when the extension has a problem with the template"""

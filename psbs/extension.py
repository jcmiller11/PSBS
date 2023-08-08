from os.path import join, dirname, basename, isfile, abspath
import glob
from importlib import import_module, util

import sys

from jinja2.exceptions import TemplateError


class Extension:
    def __init__(self, config):
        self.methods = {}
        self.filters = {}
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

    def register_filter(self, name, function):
        if name not in self.filters:
            self.filters[name] = function

    def register_post(self, function):
        self.post.append(function)

    @staticmethod
    def get_config():
        return {}

    @classmethod
    def get_extensions(cls, user_extensions=""):
        for extension in glob.glob(
            join(dirname(__file__), "extensions", "*.py")
        ):
            if isfile(extension) and not extension.endswith("__init__.py"):
                import_module(f"psbs.extensions.{basename(extension)[:-3]}")
        for extension in user_extensions:
            module_name = f"psbs.extensions.{basename(extension)[:-3].lower()}"
            spec = util.spec_from_file_location(
                module_name, abspath(extension)
            )
            if spec and spec.loader:
                module = util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
        return cls.__subclasses__()

    @classmethod
    def get_extension_configs(cls, user_extensions=""):
        config_dict = {}
        for extension in cls.get_extensions(user_extensions):
            if extension.get_config():
                config_dict[extension.__name__] = extension.get_config()
        return config_dict

    class ExtensionError(TemplateError):
        """Thrown when the extension has a problem with the template"""

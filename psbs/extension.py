"""
EXTENSION MODULE

This module provides functionality for loading and managing PSBS extensions.

"""

from os.path import join, dirname, basename, isfile, abspath
import glob
from importlib import import_module, util

import sys

from jinja2.exceptions import TemplateError


class Extension:
    """
    A class for loading and managing PSBS extensions.

    This class provides functionality for registering extension methods,
    filters, and post-processing functions, as well as loading both built-in
    and user-defined extensions.

    Args:
        config (dict): Configuration settings for the extension.

    Attributes:
        methods (dict): A dictionary to store registered extension methods.
        filters (dict): A dictionary to store registered extension filters.
        post (list): A list to store registered post-processing functions.
        config (dict): Configuration settings for the extension.

    Methods:
        register(self, name, function): Registers an extension method.
        register_filter(self, name, function): Registers an extension filter.
        register_post(self, function): Registers a post-processing function.
        get_config(cls): Returns the configuration settings for the extension.
        get_extensions(cls, user_extensions=""): Loads and returns extensions.
        get_extension_configs(cls, user_extensions=""): Returns configuration
        settings for available extensions.
    """

    def __init__(self, config):
        self.methods = {}
        self.filters = {}
        self.post = []
        # Replace missing or None config values with default values
        self.config = {
            key: value if config.get(key) is None else config.get(key, value)
            for key, value in self.get_config().items()
        }

    def register(self, name, function):
        """
        Register an extension method.

        Args:
            name (str): The name to register the method under.
            function (callable): The function to be registered.
        """
        self.methods.setdefault(name, function)

    def register_filter(self, name, function):
        """
        Register an extension filter.

        Args:
            name (str): The name to register the filter under.
            function (callable): The filter function to be registered.
        """
        self.filters.setdefault(name, function)

    def register_post(self, function):
        """
        Register a post-processing function.

        Args:
            function (callable): The post-processing function to be registered.
        """
        self.post.append(function)

    @staticmethod
    def get_config():
        """
        Get configuration settings for the extension.

        This method returns an empty dictionary by default.
        Subclasses can override this method to provide specific configuration
        settings.

        Returns:
            dict: Configuration settings for the extension.
        """
        return {}

    @classmethod
    def get_extensions(cls, user_extensions=None):
        """
        Load and return available extensions.

        Args:
            user_extensions (list, optional): List of paths to user-defined
            extension files. Defaults None.

        Returns:
            list: A list of Extension subclass instances.
        """
        import_path = join(dirname(__file__), "extensions")

        # Import built-in extensions
        for extension in glob.glob(join(import_path, "*.py")):
            if isfile(extension) and not extension.endswith("__init__.py"):
                import_module(f"psbs.extensions.{basename(extension)[:-3]}")

        # Import user-defined extensions
        if isinstance(user_extensions, str):
            user_extensions = [user_extensions]
        if user_extensions is None or not isinstance(user_extensions, list):
            user_extensions = []

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
        """
        Get configuration settings for available extensions.

        Args:
            user_extensions (list, optional): List of paths to user-defined
            extension files. Defaults to an empty list.

        Returns:
            dict: Configuration settings for available extensions.
        """
        config_dict = {}
        for extension in cls.get_extensions(user_extensions):
            if extension.get_config():
                config_dict[extension.__name__] = extension.get_config()
        return config_dict

    class ExtensionError(TemplateError):
        """Thrown when the extension has a problem with the template"""

"""
BUILD EXTENSION MODULE

This module provides an extension class related to build types such as
debugging and release builds.
"""

from psbs.extension import Extension


class Build(Extension):
    """
    A class representing a build extension for PSBS.

    This class provides functionality related to build types such as
    debugging and release builds.

    Args:
        config (dict): A configuration dictionary for the extension.

    Attributes:
        config (dict): The configuration dictionary for the extension.

    Methods:
        get_build(): Get the current build type.
        is_debug(): Check if the current build type is 'debug'.
        is_release(): Check if the current build type is 'release'.
    """

    def __init__(self, config):
        super().__init__(config)
        self.register("build", self.get_build)
        self.register("debug", self.is_debug)
        self.register("release", self.is_release)

    @staticmethod
    def get_config():
        """
        Get the default configuration for the Build extension.

        Returns:
            dict: A dictionary containing default configuration values.
        """
        return {"name": "debug"}

    def get_build(self):
        """
        Get the current build type.

        Returns:
            str: The current build type.
        """
        return self.config["name"].lower()

    def is_debug(self):
        """
        Check if the current build type is 'debug'.

        Returns:
            bool: True if current build type is 'debug', False otherwise.
        """
        return self.get_build() == "debug"

    def is_release(self):
        """
        Check if the current build type is 'release'.

        Returns:
            bool: True if current build type is 'release', False otherwise.
        """
        return self.get_build() == "release"

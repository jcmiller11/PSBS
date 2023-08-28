"""
CONFIG MODULE

This module provides functions for loading configuration settings.

"""

from .utils import read_yaml

from .extension import Extension


def get_config(config_file=None):
    """
    Get configuration settings.

    This function returns the configuration settings, which includes both
    default values and if a configuration file is provided merges them with
    the values loaded from that file.

    Args:
        config_file (str, optional): The path to the configuration file to
        load. Defaults to None.

    Returns:
        dict: The merged configuration settings.

    """
    # Define default values
    defaults = {
        "gist_id": "",
        "engine": "https://www.puzzlescript.net/",
        "template": "main.pss",
        "user_extensions": [],
    }

    defaults.update(Extension.get_extension_configs())
    # Return defaults if not loading a config file
    if not config_file:
        return defaults

    # Load the config file into a dictionary
    config_dict = read_yaml(config_file)
    user_extensions = config_dict.get("user_extensions", [])

    # Load default values from extension configs
    defaults.update(Extension.get_extension_configs(user_extensions))

    # Recursively update defaults with config_dict
    def update_dict_values(target_dict, update_dict):
        for key, value in target_dict.items():
            # Check if the key is present in the update_dict
            if key in update_dict:
                # Check if both values are dicts for recursive update
                if isinstance(value, dict) and isinstance(
                    update_dict[key], dict
                ):
                    update_dict_values(value, update_dict[key])
                else:
                    try:
                        if type(target_dict[key]) == list and type(update_dict[key]) == str:
                            update_dict[key] = [update_dict[key]]
                        if type(target_dict[key]) == str and update_dict[key] == None:
                            update_dict[key] = ""
                        if type(target_dict[key]) != type(update_dict[key]):
                            raise TypeError
                        target_dict[key] = update_dict[key]
                    except (ValueError, TypeError):
                        # If type conversion fails leave default value
                        print(
                            f"Warning: unable to read config directive {key}"
                        )
                        print("  Using default value instead")

    # Update the defaults dictionary with values from the config_dict
    update_dict_values(defaults, config_dict)
    return defaults

"""
TOKEN MANAGEMENT MODULE

This module provides functions for retrieving and setting authentication tokens.
"""

from os import path
import subprocess

from platformdirs import user_data_dir
from .utils import read_file, write_file


def get_token(verbose=False):
    """
    Get an authentication token for GitHub.

    This function first checks for a stored token in the user's data
    directory. If a stored token is found, it is returned. If not, the
    function attempts to retrieve a token using the GitHub CLI (gh-cli)
    If gh-cli is not installed or doesn't provide a token, an error is raised.

    Args:
        verbose (bool, optional): If True, print verbose messages. Defaults to
        False.

    Returns:
        str: The authentication token.
    """
    # Define the directory and file paths for the token
    token_dir = user_data_dir(appname="psbs", appauthor="psbs")
    token_file = path.join(token_dir, "token")

    # Check if the token file exists
    if path.exists(token_file):
        if verbose:
            print(f"Reading token from: {token_file}")
        return read_file(token_file)

    # Attempt to retrieve a token using gh-cli
    try:
        if verbose:
            print("Reading token from gh-cli")
        token = subprocess.check_output(
            ["gh", "auth", "token"], text=True
        ).strip()
        return token
    except FileNotFoundError as err:
        print("ERROR: gh-cli does not appear to be installed")
        raise SystemExit(1) from err
    except subprocess.CalledProcessError as err:
        print("ERROR: gh-cli refuses to provide token")
        raise SystemExit(1) from err


def set_token(token):
    """
    Set an authentication token for GitHub.

    This function stores the provided authentication token in the user's data
    directory.

    Args:
        token (str): The authentication token to be set.
    """
    # Define the directory and file paths for the token
    token_dir = user_data_dir(
        appname="psbs", appauthor="psbs", ensure_exists=True
    )
    token_file = path.join(token_dir, "token")

    # Write the token to the token file
    write_file(token_file, token)

"""
GISTER MODULE

This module provides a class for interacting with GitHub Gists.

"""

from os import path
import json
import requests
from .errors import PSBSError
from .utils import read_file
from .token import get_token


class Gister:
    """
    A class for interacting with GitHub Gists.

    This class provides methods for creating, updating, reading, and writing
    to GitHub Gists.

    Args:
        gist_id (str, optional): The ID of an existing gist. Defaults to an
        empty string.

    Attributes:
        token (str): The GitHub access token.
        gist_id (str): The ID of the existing gist.
        content (dict): The content of the existing gist.

    Methods:
        write(file): Write content to from a file to that file in the gist.
        read(file): Read content from a file in the gist.
        create(name): Create a new gist with placeholder files.
    """

    def __init__(self, gist_id=""):
        """
        Initialize the Gister instance.

        Args:
            gist_id (str, optional): The ID of an existing gist. Defaults to
            an empty string.
        """
        self.token = get_token()
        self.gist_id = gist_id
        self.content = None

    class GistError(Exception):
        """
        Exception thrown when GitHub refuses a request for some reason.
        """

    def write(self, file):
        """
        Write content to a file in the gist.

        Args:
            file (str): The path to the file to be written.

        Returns:
            requests.Response: The response from the GitHub API.
        """
        filename = path.basename(file)
        data = {"files": {filename: {"content": read_file(file)}}}
        return self.__request(data=json.dumps(data))

    def read(self, file):
        """
        Read content from a file in the gist.

        Args:
            file (str): The path to the file to be read.

        Returns:
            str: The content of the specified file in the gist.
        """
        filename = path.basename(file)
        self.content = self.content or self.__request().json()
        try:
            return self.content["files"][filename]["content"]
        except KeyError as err:
            print(f"Error: File {filename} not found in gist {self.gist_id}")
            raise SystemExit(1) from err

    def create(self, name=""):
        """
        Create a new gist with placeholder files.

        Args:
            name (str, optional): The name of the gist. Defaults to an empty
            string.

        Returns:
            str: The ID of the created Gist.
        """
        placeholder = "This project has not been built yet"
        data = {
            "description": f"{name} (PSBS Project)",
            "public": True,
            "files": {
                "readme.txt": {"content": placeholder},
                "script.txt": {"content": placeholder},
            },
        }
        response = self.__request(data=json.dumps(data), post=True).json()
        return response["id"]  # Return the ID of the created Gist

    def __request(self, data=None, post=False):
        """
        Make requests to the GitHub Gists API.

        Args:
            data (str, optional): Data to be sent with the request.
            Defaults to None.
            post (bool, optional): If True, make a POST request. If False,
            make a PATCH request. Defaults to False.

        Returns:
            requests.Response: The response from the GitHub API.
        """
        headers = {"Authorization": f"token {self.token}"}

        # URL for updating existing Gist
        query_url = f"https://api.github.com/gists/{self.gist_id}"
        try:
            if post:
                # URL for creating new Gist
                query_url = "https://api.github.com/gists"
                response = requests.post(
                    query_url, headers=headers, timeout=5, data=data
                )
            else:
                response = requests.patch(
                    query_url, headers=headers, timeout=5, data=data
                )
            # Check response status codes and handle errors
            if response.status_code == 422:
                raise self.GistError("422: Validation failed")
            if response.status_code == 404:
                raise self.GistError("404: File not found")
            if response.status_code == 403:
                raise self.GistError("403: Forbidden")
            if response.status_code >= 400:
                raise self.GistError(response)
        except (ConnectionError, requests.exceptions.ConnectionError) as err:
            raise PSBSError("Error: Unable to connect to GitHub") from err
        except self.GistError as err:
            raise PSBSError(
                f"Error: Unable to access gist\n  Response: {err}"
            ) from err
        return response

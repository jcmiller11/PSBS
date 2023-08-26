from os import path
import json
import requests
from .utils import read_file
from .token import get_token


class Gister:
    def __init__(self, gist_id=""):
        self.token = get_token()
        self.gist_id = gist_id
        self.content = None

    class GistError(Exception):
        """Thrown when GitHub refuses request for some reason"""

    def write(self, file):
        filename = path.basename(file)
        data = {"files": {filename: {"content": read_file(file)}}}
        return self.__request(data=json.dumps(data))

    def read(self, file):
        filename = path.basename(file)
        self.content = self.content or self.__request().json()
        try:
            return self.content["files"][filename]["content"]
        except KeyError as err:
            print(f"Error: File {filename} not found in gist {self.gist_id}")
            raise SystemExit(1) from err

    def create(self, name=""):
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
        except ConnectionError as err:
            print("Error: Unable to connect to GitHub")
            raise SystemExit(1) from err
        except self.GistError as err:
            print(f"Error: Unable to access gist\n  Response: {err}")
            raise SystemExit(1) from err
        return response

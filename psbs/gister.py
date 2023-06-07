from os import environ, getenv, path
import subprocess
import json
import requests
from .utils import read_file


class Gister:
    def __init__(self, gist_id):
        self.token = self.__get_token()
        self.gist_id = gist_id
        self.content = None

    class GistError(Exception):
        """Thrown when GitHub refuses request for some reason"""

    def write(self, file):
        filename = path.basename(file)
        data = {"files": {filename: {"content": read_file(file)}}}
        return self.__request(json.dumps(data))

    def read(self, file):
        filename = path.basename(file)
        if self.content is None:
            response = self.__request()
            self.content = response.json()
        try:
            file_content = self.content["files"][filename]["content"]
        except KeyError as err:
            print(f"Error: File {filename} not found in gist {self.gist_id}")
            raise SystemExit(1) from err
        return file_content

    def __request(self, data=None):
        headers = {"Authorization": f"token {self.token}"}
        query_url = f"https://api.github.com/gists/{self.gist_id}"
        try:
            response = requests.patch(
                query_url, headers=headers, timeout=5, data=data
            )
            if response.status_code == 404:
                raise self.GistError("404: File not found")
            if response.status_code == 403:
                raise self.GistError("403: Forbidden")
            if "message" in response:
                raise self.GistError(response)
        except ConnectionError as err:
            print("Error: Unable to connect to GitHub")
            raise SystemExit(1) from err
        except self.GistError as err:
            print(f"Error: Unable to access gist\n  Response: {err}")
            raise SystemExit(1) from err
        return response

    def __get_token(self):
        if "PSBS_GH_TOKEN" in environ:
            return getenv("PSBS_GH_TOKEN")
        try:
            token = subprocess.check_output(["gh", "auth", "token"])
            token = token.decode("utf-8")
            token = token.strip()
            return token
        except FileNotFoundError as err:
            print("ERROR: gh-cli does not appear to be installed")
            raise SystemExit(1) from err
        except subprocess.CalledProcessError as err:
            print("ERROR: gh-cli refuses to provide token")
            raise SystemExit(1) from err

from os import environ, getenv, path
import subprocess
import requests
import json


class Gister:
    def __init__(self, gist_id):
        self.token = self.__get_token()
        self.gist_id = gist_id

    class GistError(Exception):
        '''Thrown when GitHub refuses request for some reason'''

    def write(self, file):
        filename = path.basename(file)
        try:
            with open(file, "r", encoding='UTF-8') as content:
                data = {"files":{filename:{"content":content.read()}}}
        except IOError as err:
            print(f"Error: Config file not found\n  {err}")
            raise SystemExit(1) from err
        return self.__request(filename,data)

    def read(self, file):
        filename = path.basename(file)
        response = self.__request(file)
        resp_content = resp.json()
        return resp_content['files'][file]['content']

    def __request(self, file, data = ""):
        headers = {"Authorization": f"token {self.token}"}
        query_url = f"https://api.github.com/gists/{self.gist_id}"
        try:
            response = requests.patch(query_url, headers=headers, data=json.dumps(data))
            if response.status_code==404:
                raise self.GistError("404: File not found")
            if response.status_code==403:
                raise self.GistError("403: Forbidden")
            if response.status_code!=200:
                raise self.GistError("Reason unknown")
        except ConnectionError as err:
            print("Error: Unable to connect to GitHub")
            raise SystemExit(1) from err
        except self.GistError as err:
            print(f"Error: Unable to update gist\n  Response: {err}")
            raise SystemExit(1) from err
        return response

    def __get_token(self):
        if "PSBS_GH_TOKEN" in environ:
            return getenv('PSBS_GH_TOKEN')
        try:
            return subprocess.check_output(['gh', 'auth', 'token']).decode('utf-8').strip()
        except FileNotFoundError as err:
            print("ERROR: gh-cli does not appear to be installed, aborting upload")
            raise SystemExit(1) from err
        except subprocess.CalledProcessError as err:
            print("ERROR: gh-cli refuses to provide token, aborting upload")
            raise SystemExit(1) from err

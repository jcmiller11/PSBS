from os import path
import subprocess

from platformdirs import user_data_dir
from .utils import read_file, write_file


def get_token(verbose=False):
    token_dir = user_data_dir(appname="psbs", appauthor="psbs")
    token_file = path.join(token_dir, "token")
    if path.exists(token_file):
        if verbose:
            print(f"Reading token from: {token_file}")
        return read_file(token_file)
    try:
        if verbose:
            print("Reading token from gh-cli")
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


def set_token(token):
    token_dir = user_data_dir(
        appname="psbs", appauthor="psbs", ensure_exists=True
    )
    token_file = path.join(token_dir, "token")
    write_file(token_file, token)

import pathlib
import sys

from environs import Env

script_path = pathlib.Path(sys.argv[0]).parent.parent.parent
path = f"{script_path}\\.env"

env = Env()
env.read_env(path)

URL = env.str('API_URL')
HEADERS = {}


def url(endpoint):
    return URL + endpoint

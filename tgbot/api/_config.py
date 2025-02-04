import pathlib
import sys
import os

from environs import Env

script_path = pathlib.Path(sys.argv[0]).parent
path = f"{script_path}\\.env"

env = Env()
env.read_env(path)

URL = 'localhost:3000/'
HEADERS = {}

if "API_URL" in os.environ:
    URL = env.str('API_URL')
    HEADERS = {}


def url(endpoint):
    return URL + endpoint

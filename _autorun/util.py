import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


def get_faforever_dir():
    if os.name == "nt":
        return Path("c:ProgramData/FAForever")
    else:
        return Path.home() / ".faforever"


def confirm(message):
    res = input(message + " [Y/n]: ").strip().lower()
    while True:
        if not res or res == "y":
            return True
        elif res == "n":
            return False

        res = input("Enter one of [Y/n]: ").strip().lower()


def walk(path):
    for root, _, files in os.walk(path):
        for filename in files:
            yield os.path.join(root, filename)


def zip_add_dir(f, dir):
    for file in walk(dir):
        log.debug("Adding %s", file)
        f.write(file)

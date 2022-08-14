import os
import sys
from threading import Thread
from typing import Callable


# metadata
__version__ = (0, 12, 0)
__author__ = 'Faraphel'


# external links
discord_url = "https://discord.gg/HEYW5v8ZCd"
github_wiki_url = "https://github.com/Faraphel/MKWF-Install/wiki/help"
readthedocs_url = "https://mkwf-install.readthedocs.io/"


# constant declaration
Ko: int = 1_000
Mo: int = 1_000 * Ko
Go: int = 1_000 * Mo

minimum_space_available: int = 15*Go


# global type hint
TemplateSafeEval: str
TemplateMultipleSafeEval: str
Env: dict[str, any]


# useful functions
def threaded(func: Callable) -> Callable:
    """
    Decorate a function to run in a separate thread
    :param func: a function
    :return: the decorated function
    """

    def wrapper(*args, **kwargs):
        # run the function in a Daemon, so it will stop when the main thread stops
        thread = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread

    return wrapper


def restart_program():
    """
    Restart the program
    """
    os.execl(sys.executable, sys.executable, *sys.argv)

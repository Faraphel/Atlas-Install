import os
import sys
from threading import Thread
from typing import Callable


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


def comp_dict_changes(d_old: dict, d_new: dict) -> dict:
    """
    Return a comparaison dict showing every value that changed between d_old and d_new. Deleted value are ignored.
    Example : {"a": 1, "b": 3, "d": 13}, {"b": 2, "c": 10, "d": 13} -> {"b": 2, "c": 10}
    """
    return {name: value for name, value in d_new.items() if d_old.get(name) != value}

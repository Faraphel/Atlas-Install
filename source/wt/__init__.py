import subprocess
from pathlib import Path
from typing import Callable

from source import system
from source.translation import translate as _


tools_dir: Path = Path("./tools/")

subprocess_kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if system == "win64" else {}
# creationflags are Windows specific. Linux don't show any subprocess window per default.


class WTError(Exception):
    def __init__(self, tools_path: Path | str, return_code: int):
        try:
            error = subprocess.run(
                [tools_path, "ERROR", str(return_code)],
                stdout=subprocess.PIPE,
                check=True,
                **subprocess_kwargs
            ).stdout.decode()
        except subprocess.CalledProcessError:
            error = _("ERROR_CANNOT_GET_ERROR_MESSAGE")

        super().__init__(_("ERROR_WT") % (tools_path, return_code, error))


class MissingWTError(Exception):
    def __init__(self, tool_name: str):
        super().__init__(_("ERROR_CANNOT_FIND_TOOL") % tool_name)


try: tools_szs_dir = next(tools_dir.glob("./szs*/")) / system
except StopIteration as e: raise MissingWTError("szs") from e

try: tools_wit_dir = next(tools_dir.glob("./wit*/")) / system
except StopIteration as e: raise MissingWTError("wit") from e


def better_wt_error(tools_path: Path | str):
    """
    Raise a better error when the subprocess return with a non 0 value.
    :param tools_path: path of the used tools
    :return: wrapper
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except subprocess.CalledProcessError as e:
                raise WTError(tools_path, e.returncode) from e

        return wrapper

    return decorator


def _run(tools_path: Path | str, *args, **kwargs) -> bytes:
    """
    Run a command and return the output
    :param args: command arguments
    :return: the output of the command
    """
    return subprocess.run(
        [tools_path, *args],
        stdout=subprocess.PIPE,
        check=True,
        **subprocess_kwargs
    ).stdout


def get_tools_run_function(tools_path: Path | str) -> Callable:
    """
    Return a new function with the tool argument already entered
    :param tools_path: path to the tool
    :return: new function
    """
    return lambda *args, **kwargs: better_wt_error(tools_path)(_run)(tools_path, *args, **kwargs)


def _run_dict(tools_path: Path | str, *args, **kwargs) -> dict:
    """
    Return a dictionary of a command that return value associated to a key with a equal sign
    :param tools_path: tools to use
    :param command: command to use
    :param args: other args to use
    :return: the according dictionary
    """
    d = {}
    for line in filter(lambda f: "=" in f, _run(tools_path, *args).decode().splitlines()):
        key, value = line.split("=", 1)
        value = value.strip()

        # if the value represent a string
        if value.startswith('"') and value.endswith('"'): value = value.strip('"').strip()
        # else if the value represent a float
        elif "." in value: value = float(value)
        # else the value represent a int
        else: value = int(value)

        d[key.strip()] = value

    return d


def get_tools_run_dict_function(tools_path: Path | str) -> Callable:
    """
    Return a new function with the tool argument already entered
    :param tools_path: path to the tool
    :return: new function
    """
    return lambda *args, **kwargs: better_wt_error(tools_path)(_run_dict)(tools_path, *args, **kwargs)


def _run_popen(tools_path: Path | str, *args, universal_newlines=False) -> subprocess.Popen:
    """
    Run a command and return the process
    :param args: command arguments
    :return: the output of the command
    """
    return subprocess.Popen(
        [tools_path, *args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=1 if universal_newlines else None,
        universal_newlines=universal_newlines,
        **subprocess_kwargs
    )


def get_tools_run_popen_function(tools_path: Path | str) -> Callable:
    """
    Return a new function with the tool argument already entered
    :param tools_path: path to the tool
    :return: new function
    """
    return lambda *args, **kwargs: _run_popen(tools_path, *args, **kwargs)

import subprocess
from pathlib import Path
import os


class WTError(Exception):
    def __init__(self, tools_path: Path | str, return_code: int):
        try:
            error = subprocess.run(
                [tools_path, "ERROR", str(return_code)],
                stdout=subprocess.PIPE,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            ).stdout.decode()
        except subprocess.CalledProcessError as e:
            error = "- Can't get the error message -"

        super().__init__(f"{tools_path} raised {return_code} :\n{error}\n")


class MissingWTError(Exception):
    def __init__(self, tool_name: str):
        super().__init__(f"Can't find tools \"{tool_name}\" in the tools directory.")


tools_dir = Path("./tools/")
system = "win64" if os.name == "nt" else "lin64"


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


def _run(tools_path: Path | str, *args) -> bytes:
    """
    Run a command and return the output
    :param args: command arguments
    :return: the output of the command
    """
    return subprocess.run(
        [tools_path, *args],
        stdout=subprocess.PIPE,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    ).stdout


def _run_dict(tools_path: Path | str, *args) -> dict:
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
        creationflags=subprocess.CREATE_NO_WINDOW,
        bufsize=1 if universal_newlines else None,
        universal_newlines=universal_newlines,
    )

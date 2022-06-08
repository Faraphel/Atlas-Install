import subprocess
from pathlib import Path

tools_szs_dir = Path("./tools/szs/")
tools_wit_dir = Path("./tools/wit/")


class WTError(Exception):
    def __init__(self, tool_path: Path, return_code: int):
        try:
            error = subprocess.run(
                [tool_path, "ERROR", str(return_code)],
                stdout=subprocess.PIPE,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            ).stdout.decode()
        except subprocess.CalledProcessError as e:
            error = "- Can't get the error message -"

        super().__init__(f"{tool_path} raised {return_code} :\n{error}\n")


def better_error(tool_path: Path):
    """
    Raise a better error when the subprocess return with a non 0 value.
    :param tool_path: path of the used tools
    :return: wrapper
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except subprocess.CalledProcessError as e:
                raise WTError(tool_path, e.returncode) from e

        return wrapper

    return decorator

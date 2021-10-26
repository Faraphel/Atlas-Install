import subprocess
from . import error

WSTRT_PATH = "./tools/szs/wstrt"


@error.better_wszst_error(wszst_tools=WSTRT_PATH)
def patch(path: str) -> None:
    """
    Patch the main.dol file
    :param path: path to the game
    """
    subprocess.run([WSTRT_PATH, "patch", path + "/sys/main.dol", "--clean-dol", "--add-lecode"],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
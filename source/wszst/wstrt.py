import subprocess


def patch(path: str) -> None:
    """
    Patch the main.dol file
    :param path: path to the game
    """
    subprocess.run(["./tools/szs/wstrt", "patch", path + "/sys/main.dol", "--clean-dol", "--add-lecode"],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
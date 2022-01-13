import subprocess
from . import error

WSTRT_PATH = "./tools/szs/wstrt"


@error.better_wszst_error(wszst_tools=WSTRT_PATH)
def patch(path: str, region_id: int = None) -> None:
    """
    Patch the main.dol file
    :param region_id: optional option to the mod region
    :param path: path to the game
    """

    cmd = [
        WSTRT_PATH, "patch",
        path + "/sys/main.dol", path + "/files/rel/StaticR.rel",
        "--clean-dol",
        "--add-lecode"
    ]
    if region_id: cmd.extend(["--region", str(region_id)])

    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
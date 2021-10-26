import subprocess
from . import error

WBMGT_PATH = "./tools/szs/wbmgt"


@error.better_wszst_error(wszst_tools=WBMGT_PATH)
def encode(file: str) -> None:
    """
    Encode a txt file into a bmg file
    :param file: txt file to convert
    """
    subprocess.run([WBMGT_PATH, "ENCODE", file, "--overwrite"],
                   creationflags=subprocess.CREATE_NO_WINDOW)


@error.better_wszst_error(wszst_tools=WBMGT_PATH)
def cat(path: str, subfile: str = ".d/message/Common.bmg") -> str:
    """
    read a bmg file
    :param path: path to a szs file
    :param subfile: path to a subdirectory
    :return: bmg definition
    """
    return subprocess.run([WBMGT_PATH, "CAT", path + subfile],
                          creationflags=subprocess.CREATE_NO_WINDOW,
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()

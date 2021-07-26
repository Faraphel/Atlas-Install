from . import *


def encode(file: str) -> None:
    """
    Encode a txt file into a bmg file
    :param file: txt file to convert
    """
    subprocess.run(["./tools/szs/wbmgt", "ENCODE", file, "--overwrite"],
                   creationflags=CREATE_NO_WINDOW)


def cat(path: str, subfile: str = ".d/message/Common.bmg") -> str:
    """
    read a bmg file
    :param path: path to a szs file
    :param subfile: path to a subdirectory
    :return: bmg definition
    """
    return subprocess.run(["./tools/szs/wbmgt", "CAT", path + subfile],
                          creationflags=CREATE_NO_WINDOW,
                          check=True, stdout=subprocess.PIPE).stdout.decode()
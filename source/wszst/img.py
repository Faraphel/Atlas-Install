from . import *


def encode(src_file: str, format: str) -> None:
    """
    Encode an .png image into a new format
    :param src_file: .png image
    :param format: new image format
    """
    subprocess.run(["./tools/szs/wimgt", "ENCODE", src_file, "-x", format, "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)

import subprocess
from . import error

WIMGT_PATH = "./tools/szs/wimgt"


@error.better_wszst_error(wszst_tools=WIMGT_PATH)
def encode(file: str, format: str) -> None:
    """
    Encode an .png image into a new format
    :param file: .png image
    :param format: new image format
    """
    subprocess.run([WIMGT_PATH, "ENCODE", file, "-x", format, "--overwrite"],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)

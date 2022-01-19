import subprocess
from . import error

WIMGT_PATH = "./tools/szs/wimgt"


@error.better_wszst_error(wszst_tools=WIMGT_PATH)
def encode(file: str, format: str, dest_file: str = None) -> None:
    """
    Encode an .png image into a new format
    :param dest_file: destination
    :param file: .png image
    :param format: new image format
    """
    cmd = [WIMGT_PATH, "ENCODE", file, "-x", format, "--overwrite"]
    if dest_file: cmd.extend(["--DEST", dest_file])
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)

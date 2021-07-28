import subprocess


def encode(file: str, format: str) -> None:
    """
    Encode an .png image into a new format
    :param file: .png image
    :param format: new image format
    """
    subprocess.run(["./tools/szs/wimgt", "ENCODE", file, "-x", format, "--overwrite"],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)

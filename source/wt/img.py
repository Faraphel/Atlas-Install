from source.wt import *

tools_path = tools_szs_dir / ("wimgt.exe" if system == "win64" else "wimgt")


_tools_run = get_tools_run_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


@better_wt_error(tools_path)
def encode_data(image_data: bytes, transform: str = "CMPR") -> bytes:
    """
    Convert the image data and return the encoded image data
    :param image_data: the original image data
    :param transform: the type of the image encoding
    :return: the encoded image data
    """
    process = _tools_run_popen("ENCODE", "-", "--transform", transform, "--DEST", "-")
    stdout, _ = process.communicate(input=image_data)

    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout


@better_wt_error(tools_path)
def decode_data(image_data: bytes) -> bytes:
    """
    Convert the game image data and return the decoded image data
    :param image_data: the original game image data
    :return: the decoded image data
    """
    process = _tools_run_popen("DECODE", "-", "--DEST", "-")
    stdout, _ = process.communicate(input=image_data)

    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout


class IMGPath:
    """
    Represent a path to a normal image, that can be converted into game image data
    """
    __slots__ = ("path", )

    def __init__(self, path: Path | str):
        self.path: Path = Path(path)

    def get_encoded_data(self, transform: str = "CMPR") -> bytes:
        """
        Convert the image and return the encoded image data
        :transform: the type of the image encoding
        :return: the data of the encoded image
        """
        # using "-" for destination allow for output in the stdout
        return _tools_run("ENCODE", self.path, "--transform", transform, "--DEST", "-")


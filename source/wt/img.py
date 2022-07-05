from source.wt import *
from source.wt import _run

tools_path = tools_szs_dir / ("wimgt.exe" if system == "win64" else "wimgt")


@better_wt_error(tools_path)
class IMGPath:
    """
    Represent a path to an image
    """
    __slots__ = ("path", )

    def __init__(self, path: Path | str):
        self.path: Path = Path(path)

    @better_wt_error(tools_path)
    def _run(self, *args) -> bytes:
        """
        Return a command with wszst and return the output
        :param args: command arguments
        :return: the output of the command
        """
        return _run(tools_path, *args)

    def get_encoded_data(self, transform: str = "CMPR") -> bytes:
        """
        Convert the image return the encoded image data
        :transform: the type of the image encoding
        :return: the data of the encoded image
        """
        # using "-" for destination allow for output in the stdout
        return self._run("ENCODE", self.path, "--transform", transform, "--DEST", "-")

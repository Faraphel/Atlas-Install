from source.wt import *
from source.wt import _run

tools_path = tools_szs_dir / ("wimgt.exe" if system == "win64" else "wimgt")


@better_wt_error(tools_path)
class BMGPath:
    """
    Represent a path to a bmg file (game file containing text data)
    """
    __slots__ = ("path",)

    def __init__(self, path: Path | str):
        self.path: Path = Path(path)

    @better_wt_error(tools_path)
    def _run(self, *args) -> bytes:
        """
        Return a command with wbmgt and return the output
        :param args: command arguments
        :return: the output of the command
        """
        return _run(tools_path, *args)

    def get_decoded_data(self):
        """
        Return the decoded content of the bmg file
        :return:
        """
        return self._run("DECODE", self.path, "--DEST", "-")

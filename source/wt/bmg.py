from source.wt import *

tools_path = tools_szs_dir / ("wimgt.exe" if system == "win64" else "wimgt")


_tools_run = get_tools_run_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


class BMGPath:
    """
    Represent a path to a bmg file (game file containing text data)
    """
    __slots__ = ("path",)

    def __init__(self, path: Path | str):
        self.path: Path = Path(path)

    def get_decoded_data(self):
        """
        Return the decoded content of the bmg file
        :return:
        """
        return _tools_run("DECODE", self.path, "--DEST", "-")


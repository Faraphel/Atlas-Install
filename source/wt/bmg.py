from source.wt import *
from source.wt import _run, _run_popen

tools_path = tools_szs_dir / ("wimgt.exe" if system == "win64" else "wimgt")


@better_wt_error(tools_path)
def _tools_run(*args) -> bytes:
    """
    Return a command with wbmgt and return the output
    :param args: command arguments
    :return: the output of the command
    """
    return _run(tools_path, *args)


def _tools_run_popen(*args, **kwargs) -> subprocess.Popen:
    """
    Return a popen of command with wbmgt
    :param args: command arguments
    :return: the process of the command
    """
    return _run_popen(tools_path, *args, **kwargs)


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


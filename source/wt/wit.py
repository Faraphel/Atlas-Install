from source.wt import *
from source.wt import _run, _run_dict

tools_path = tools_wit_dir / ("wit.exe" if system == "win64" else "wit")


class WITPath:
    __slots__ = ("path",)

    def __init__(self, path: Path):
        self.path = path

    @better_error(tools_path)
    def _run(self, *args) -> bytes:
        """
        Return a command with wit and return the output
        :param args: command arguments
        :return: the output of the command
        """
        return _run(tools_path, *args)

    @better_error(tools_path)
    def _run_dict(self, *args) -> dict:
        """
        Return a dictionary of a command that return value associated to a key with a equal sign
        :param args: others arguments
        :return: the dictionary
        """
        return _run_dict(tools_path, *args)

    def analyze(self) -> dict:
        """
        Return the analyze of the file
        :return: dictionnary of key and value of the analyze
        """
        return self._run_dict("ANALYZE", self.path)

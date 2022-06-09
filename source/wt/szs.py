from source.wt import *
from source.wt import _run, _run_dict

tools_path = tools_szs_dir / "wszst.exe"


class SZSPath:
    __slots__ = ("path",)

    def __init__(self, path: Path | str):
        self.path: Path = path if isinstance(path, Path) else Path(path)

    def __repr__(self):
        return f"<SZSPath: {self.path}>"

    @better_error(tools_path)
    def _run(self, *args) -> bytes:
        """
        Return a command with wszst and return the output
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

    def cat(self, subfile: str) -> bytes:
        """
        Run the cat command (read a subfile) and return the output
        :param subfile: subfile name
        :return: the content of the subfile
        """
        return self._run("cat", self.path / subfile)

    def extract(self, subfile: str, dest: Path | str) -> Path:
        """
        Extract a subfile to a destination
        :param subfile: subfile name
        :param dest: destination path
        :return: the extracted file path
        """
        return self[subfile].extract(dest)

    def extract_all(self, dest: Path | str) -> Path:
        """
        Extract all the subfiles to a destination
        :param dest: output directory
        :return:
        """
        dest: Path = dest if isinstance(dest, Path) else Path(dest)
        if dest.is_dir(): dest /= self.path.name

        self._run("EXTRACT", self.path, "-d", dest)
        return dest

    def analyze(self) -> dict:
        """
        Return the analyze of the szs
        :return: dictionnary of key and value of the analyze
        """
        return self._run_dict("ANALYZE", self.path)

    def list_raw(self) -> list[str]:
        """
        Return the list of subfiles
        :return: the list of subfiles
        """

        # cycle though all of the output line of the command, check if the line are empty, and if not,
        # add it to the list. Finally, remove the first line because this is a description of the command
        return [subfile.strip() for subfile in self._run("list", self.path).decode().splitlines() if subfile][1:]

    def list(self) -> list["SZSSubPath"]:
        """
        Return the list of subfiles
        :return: the list of subfiles
        """
        return [self.get_subfile(subfile) for subfile in self.list_raw()]

    def get_subfile(self, subfile: str) -> "SZSSubPath":
        """
        Return the subfile of the szs
        :return: the subfile
        """
        return SZSSubPath(self, subfile)

    def __getitem__(self, item):
        return self.get_subfile(item)

    def __iter__(self):
        return iter(self.list())


class SZSSubPath:
    __slots__ = ("szs_path", "subfile")

    def __init__(self, szs_path: SZSPath, subfile: str):
        self.szs_path = szs_path
        self.subfile = subfile

    def __repr__(self):
        return f"<SZSSubPath: {self.szs_path.path}/{self.subfile}>"

    def extract(self, dest: Path | str) -> Path:
        """
        Extract the subfile to a destination
        :param dest: destination path
        :return: the extracted file path
        """
        if self.is_dir(): raise ValueError("Can't extract a directory")

        dest: Path = dest if isinstance(dest, Path) else Path(dest)
        if dest.is_dir(): dest /= self.basename()

        with dest.open("wb") as file:
            file.write(self.szs_path.cat(self.subfile))

        return dest

    def is_dir(self):
        return self.subfile.endswith("/")

    def is_file(self):
        return not self.is_dir()

    def basename(self):
        return self.subfile.rsplit("/", 1)[-1]

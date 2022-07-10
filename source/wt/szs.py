from source.wt import *
from source.wt import _run, _run_dict

tools_path = tools_szs_dir / ("wszst.exe" if system == "win64" else "wszst")


@better_wt_error(tools_path)
def _tools_run(*args) -> bytes:
    """
    Return a command with wszst and return the output
    :param args: command arguments
    :return: the output of the command
    """
    return _run(tools_path, *args)


@better_wt_error(tools_path)
def _tools_run_dict(*args) -> dict:
    """
    Return a dictionary of a command that return value associated to a key with a equal sign
    :param args: others arguments
    :return: the dictionary
    """
    return _run_dict(tools_path, *args)


@better_wt_error(tools_path)
def autoadd(course_directory: Path | str, destination_path: Path | str) -> Path:
    """
    Extract all the autoadd files from course_directory to destination_path
    :param course_directory: directory with all the default tracks of the game
    :param destination_path: directory where the autoadd files will be extracted
    :return: directory where the autoadd files were extracted
    """
    destination_path = Path(destination_path)
    _run(tools_path, "AUTOADD", course_directory, "-D", destination_path)
    return destination_path


class SZSPath:
    __slots__ = ("path", "_analyze")

    def __init__(self, path: Path | str):
        self.path: Path = Path(path)
        self._analyze = None

    def __repr__(self) -> str:
        return f"<SZSPath: {self.path}>"

    def __eq__(self, other: "SZSPath") -> bool:
        return self.path == other.path

    def cat(self, subfile: str) -> bytes:
        """
        Run the cat command (read a subfile) and return the output
        :param subfile: subfile name
        :return: the content of the subfile
        """
        return _tools_run("cat", self.path / subfile)

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
        dest: Path = Path(dest)
        if dest.is_dir(): dest /= self.path.name

        _tools_run("EXTRACT", self.path, "-D", dest)
        return dest

    def analyze(self) -> dict:
        """
        Return the analyze of the file
        :return: dictionnary of key and value of the analyze
        """
        if self._analyze is None: self._analyze = _tools_run_dict("ANALYZE", self.path)
        return self._analyze

    def list_raw(self) -> list[str]:
        """
        Return the list of subfiles
        :return: the list of subfiles
        """

        # cycle though all of the output line of the command, check if the line are empty, and if not,
        # add it to the list. Finally, remove the first line because this is a description of the command
        return [
            subfile.strip()
            for subfile in _tools_run("list", self.path).decode().splitlines()
            if subfile.startswith("./")
        ]

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

    def __repr__(self) -> str:
        return f"<SZSSubPath: {self.szs_path.path}/{self.subfile}>"

    def __eq__(self, other: "SZSSubPath") -> bool:
        return self.subfile == other.subfile and self.szs_path == other.szs_path

    def extract(self, dest: Path | str) -> Path:
        """
        Extract the subfile to a destination
        :param dest: destination path
        :return: the extracted file path
        """
        if self.is_dir(): raise ValueError("Can't extract a directory")

        dest: Path = Path(dest)
        if dest.is_dir(): dest /= self.basename()

        with dest.open("wb") as file:
            file.write(self.szs_path.cat(self.subfile))

        return dest

    def exists(self):
        """
        Return if the subfile exist in the szs
        :return: True if the subfile exist, else otherwise
        """
        return self in self.szs_path.list()

    def is_dir(self) -> bool:
        """
        Return if the subfile is a directory
        :return: True if the subfile is a directory, else otherwise
        """
        return self.subfile.endswith("/")

    def is_file(self) -> bool:
        """
        Return if the subfile is a file
        :return: True if the subfile is a file, else otherwise
        """
        return not self.is_dir()

    def basename(self) -> str:
        """
        Return the basename of the subfile
        :return: the basename of the subfile
        """
        return self.subfile.rsplit("/", 1)[-1]

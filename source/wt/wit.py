import re
import shutil
from typing import Generator

from source.mkw.collection.Extension import Extension
from source.mkw.collection.Region import Region
from source.wt import *

tools_path = tools_wit_dir / "wit"


_tools_run = get_tools_run_function(tools_path)
_tools_run_dict = get_tools_run_dict_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


def copy(source_directory: Path | str, destination_file: Path | str) -> "WITPath":
    """
    Copy a game directory to a game file with a specific format.
    :param source_directory: path to the extracted game
    :param destination_file: path to the destination game
    :return: the destination game path
    """
    _tools_run("COPY", source_directory, "--DEST", destination_file)
    return WITPath(destination_file)


class WITPath:
    __slots__ = ("path", "_analyze")

    def __init__(self, path: Path | str):
        self.path: Path = path if isinstance(path, Path) else Path(path)
        self._analyze = None

    def __repr__(self) -> str:
        return f"<WITPath: {self.path}>"

    def __eq__(self, other: "WITPath") -> bool:
        return self.path == other.path

    def _get_fst_root(self) -> Path:
        """
        If the game is a FST, return the root of the FST
        :return: root of the FST
        """
        # main.dol is located in ./sys/main.dol, so return parent of parent
        if self.extension == Extension.FST: return self.path.parent.parent

    def edit(self, name: str = None, game_id: str = None) -> None:
        """
        Edit the game's information. If the game is a directory, this is ignored.
        """
        if self.extension == Extension.FST: return

        args = []
        if name is not None: args.extend(["--name", name])
        if game_id is not None: args.extend(["--id", game_id])

        _tools_run("EDIT", self.path, *args)

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
        if self.extension == Extension.FST:
            return [
                str(file.relative_to(self._get_fst_root()))
                for file in self._get_fst_root().rglob("*")
            ]

        return [
            subfile.strip() for subfile
            in _tools_run("files", self.path).decode().splitlines()
            if subfile.startswith("./")
        ]

    def list(self) -> list["WITSubPath"]:
        """
        Return the list of subfiles
        :return: the list of subfiles
        """
        return [self.get_subfile(subfile) for subfile in self.list_raw()]

    def get_subfile(self, subfile: str) -> "WITSubPath":
        """
        Return the subfile of the game
        :return: the subfile
        """
        return WITSubPath(self, subfile)

    def __getitem__(self, item):
        return self.get_subfile(item)

    def __iter__(self):
        return iter(self.list())

    def extract_all(self, dest: Path | str) -> Path:
        """
        Extract all the subfiles to the destination directory
        :param dest: destination directory
        :return: the extracted file path
        """
        return self["./"].extract(dest, flat=False)

    def progress_extract_all(self, dest: Path | str) -> Generator[dict, None, Path]:
        """
        Extract all the subfiles to the destination directory, yelling the percentage and the estimated time remaining
        :param dest: destination directory
        :return: the extracted file path
        """
        if self.extension == Extension.FST:
            yield {}
            shutil.copytree(self._get_fst_root(), dest)

        else:
            process = _tools_run_popen(
                "EXTRACT", self.path,
                "--DEST", dest,
                "--progress",
                "--psel=DATA",  # only extract the game data, ignore update data, ...
                universal_newlines=True
            )
            # universal_newlines is required to correctly read text line by line

            while process.poll() is None:
                m = re.match(r'\s*(?P<percentage>\d*)%(?:.*?ETA (?P<estimation>\d*:\d*))?\s*', process.stdout.readline())
                if m:
                    yield {
                        "percentage": int(m.group("percentage")),
                        "estimation": m.group("estimation")
                    }

            if process.returncode != 0:
                raise WTError(tools_path, process.returncode)

        return dest

    @property
    def extension(self) -> Extension:
        """
        Returns the extension of the game
        :return: the extension of the game
        """
        return Extension(self.path.suffix)

    @property
    def id(self) -> str:
        """
        Return the id of the game (RMCP01, RMCK01, ...)
        :return: the id of the game
        """
        return self.analyze()["id6"]

    @property
    def region(self) -> Region:
        """
        Return the region of the game (PAL, USA, EUR, ...)
        :return: the region of the game
        """
        return Region(self.analyze()["dol_region"])


class WITSubPath:
    __slots__ = ("wit_path", "subfile")

    def __init__(self, wit_path: WITPath, subfile: str):
        self.wit_path = wit_path
        self.subfile = subfile.removeprefix("./").replace("\\", "/")

    def __repr__(self):
        if self.wit_path.extension == Extension.FST: return f"<WITSubPath: {self._get_fst_path()}>"
        return f"<WITSubPath: {self.wit_path.path}/{self.subfile}>"

    def __eq__(self, other: "WITSubPath") -> bool:
        return self.subfile == other.subfile and self.wit_path == other.wit_path

    def _get_fst_path(self) -> Path:
        """
        Return the path of the subfile in the FST
        :return: the path of the subfile in the FST
        """
        return self.wit_path._get_fst_root() / self.subfile

    def extract(self, dest: Path | str, flat: bool = True) -> Path:
        """
        Extract the subfile to the destination directory
        :param flat: all files will be extracted directly in the directory, instead of creating subdirectory
        :param dest: destination directory
        :return: the extracted file path
        """
        dest: Path = Path(dest)

        if self.wit_path.extension == Extension.FST:
            # if flat is used, extract the file / dir into the destination directory, without subdirectory
            if flat:
                dest.mkdir(parents=True, exist_ok=True)
                # if we are extracting a directory, we need to extract every file recursively
                if self.is_dir():
                    for file in (self._get_fst_path()).rglob("*"):
                        if file.is_file(): shutil.copy(file, dest / file.name)
                # else we just copy the file
                else:
                    shutil.copy(self._get_fst_path(), dest)
            # if flat is not used, copy the structure of the directory, or just copy the file
            else:
                func = shutil.copytree if self.is_dir() else shutil.copy
                func(self._get_fst_path(), dest / self.subfile)

            return dest / self.basename()

        else:
            args = []
            if flat: args.append("--flat")
            _tools_run("EXTRACT", self.wit_path.path, f"--files=+{self.subfile}", "-d", dest, *args)
            return dest / self.basename()

    def is_dir(self) -> bool:
        """
        Return if the subfile is a directory
        :return: True if the subfile is a directory, else otherwise
        """
        if self.wit_path.extension == Extension.FST:
            return self._get_fst_path().is_dir()
        return self.subfile.endswith("/")

    def is_file(self) -> bool:
        """
        Return if the subfile is a file
        :return: True if the subfile is a file, else otherwise
        """
        return not self.is_dir()

    def exists(self):
        """
        Return if the subfile exist in the game
        :return: True if the subfile exist, else otherwise
        """
        return self in self.wit_path.list()

    def basename(self) -> str:
        """
        Return the basename of the subfile
        :return: the basename of the subfile
        """
        return self.subfile.rsplit("/", 1)[-1]

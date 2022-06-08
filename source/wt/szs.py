from source.wt import *

tools_path = tools_szs_dir / "wszst.exe"


class SZSPath:

    def __init__(self, path: Path | str):
        self.path: Path = path if isinstance(path, Path) else Path(path)

    @better_error(tools_path)
    def _run(self, *args) -> bytes:
        """
        Return a command with wszst and return the output
        :param args: command arguments
        :return: the output of the command
        """
        return subprocess.run(
            [tools_path, *args],
            stdout=subprocess.PIPE,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        ).stdout

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
        dest = dest if isinstance(dest, Path) else Path(dest)
        with dest.open("wb") as file:
            file.write(self.cat(subfile))

        return dest

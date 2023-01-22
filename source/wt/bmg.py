from source.wt import *

tools_path = tools_szs_dir / "wbmgt"


_tools_run = get_tools_run_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


def decode_data(bmg_data: bytes) -> str:
    """
    Decode a bmg file content into a txt content
    """
    process = _tools_run_popen("DECODE", "-", "--single-line", "--DEST", "-")
    stdout, _ = process.communicate(input=bmg_data)
    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout.decode("utf-8")


def encode_data(txt_data: str) -> bytes:
    """
    Encode a txt file content into a bmg content
    """
    process = _tools_run_popen("ENCODE", "-", "--DEST", "-")
    stdout, _ = process.communicate(input=txt_data.encode("utf-8"))
    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout


def cat_data(txt_data: str, patchs: list[str] = None, filters: list[str] = None) -> str:
    """
    Patch and filter a bmgtxt file (for example LE-COPY).
    :patchs: dictionary of patchs bmg key and value
    """
    args = []

    for filter_ in filters if filters is not None else []:
        args.extend(["--filter-bmg", filter_])

    for patch in patchs if patchs is not None else []:
        args.extend(["--patch-bmg", patch])

    process = _tools_run_popen("CAT", "-", *args)
    stdout, _ = process.communicate(input=txt_data.encode("utf-8"))
    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout.decode("utf-8")


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


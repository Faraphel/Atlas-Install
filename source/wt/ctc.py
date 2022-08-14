from source.mkw.OriginalTrack import OriginalTrack
from source.wt import *
import re

tools_path = tools_szs_dir / "wctct"


_tools_run = get_tools_run_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


def bmg_ctfile(ctfile: "Path | str") -> str:
    """
    get a bmg definition from a ctfile
    :param ctfile: the ctfile
    :return: a bmg definition
    """

    process = _tools_run_popen("BMG", "-", "--lecode")
    stdout, _ = process.communicate(input=ctfile.encode("utf-8"))
    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    # this command will generate unwanted definition for the originals tracks / arena. Delete them if
    # they are not custom

    original_tracks_texts: list[str] = list(map(lambda data: data["name"], OriginalTrack.all_original_tracks))

    def remove_unwanted_definition(match: re.Match) -> str:
        def_id = int(match.group("id"), 16)
        def_text = match.group("value").removesuffix("\r")

        # if the definition is a track / arena definition and the text is not modified, remove the definition
        if 0x7000 <= def_id <= 0x7029 and def_text in original_tracks_texts: return ""
        # otherwise, keep the line
        return match.group()

    return re.sub(r" {2}(?P<id>.*?)\t= (?P<value>.*)", remove_unwanted_definition, stdout.decode("utf-8"))

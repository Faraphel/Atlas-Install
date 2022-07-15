from source.wt import *

tools_path = tools_szs_dir / "wlect"


_tools_run = get_tools_run_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


def patch_data(lecode_data: bytes, game_tracks_directory: Path | str,
               copy_tracks_directory: Path | str, move_tracks_directory: Path | str,
               ct_file: Path | str, lpar: Path | str) -> bytes:
    """
    Patch a LECODE.bin file content
    :param lpar: parameter that can be applied to the lecode configuration
    :param ct_file: file defining track and arena slots
    :param move_tracks_directory: tracks to move inside the game
    :param copy_tracks_directory: tracks to copy inside the game
    :param game_tracks_directory: directory to all the game tracks
    :param lecode_data: LECODE.bin file content
    :return: patched LECODE.bin file content
    """
    args = []
    # TODO: implement args

    process = _tools_run_popen("PATCH", "-", "--DEST", "-", *args)
    stdout, _ = process.communicate(input=lecode_data)
    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout

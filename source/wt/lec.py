from source.wt import *

tools_path = tools_szs_dir / "wlect"


_tools_run = get_tools_run_function(tools_path)


def patch(lecode_file: "Path | str", ct_file: Path | str, lpar: Path | str,
          game_tracks_directory: Path | str = None,
          copy_tracks_directories: list[Path | str] = None,
          move_tracks_directories: list[Path | str] = None,
    ) -> Path:
    """
    Patch a LECODE.bin file content
    :param lpar: parameter that can be applied to the lecode configuration
    :param ct_file: file defining track and arena slots
    :param move_tracks_directories: tracks to move inside the game
    :param copy_tracks_directories: tracks to copy inside the game
    :param game_tracks_directory: directory to all the game tracks
    :param lecode_file: LECODE.bin file
    :return: path to the patched LECODE file
    """
    args = []
    if game_tracks_directory is not None: args.extend(["--track-dir", game_tracks_directory])
    for copy_tracks_directory in copy_tracks_directories if copy_tracks_directories is not None else []:
        args.extend(["--copy-tracks", copy_tracks_directory])
    for move_tracks_directory in move_tracks_directories if move_tracks_directories is not None else []:
        args.extend(["--move-tracks", move_tracks_directory])

    _tools_run("PATCH", lecode_file, "--le-define", ct_file, "--lpar", lpar, "--overwrite", *args)
    return Path(lecode_file)

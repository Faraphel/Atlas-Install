import subprocess
from . import error

WLECT_PATH = "./tools/szs/wlect"


@error.better_wszst_error(wszst_tools=WLECT_PATH)
def patch(lecode_file: str = f"./file/lecode-PAL.bin",
          dest_lecode_file: str = f"./files/rel/lecode-PAL.bin",
          game_track_path: str = "./files/Race/Course/",
          copy_track_paths: list = None,
          move_track_paths: list = None,
          ctfile_path: str = "./file/CTFILE.txt",
          lpar_path: str = "./file/lpar-normal.txt") -> None:
    """
    Patch the file with a lecode file (this is the adding track part)
    :param lecode_file: path to the lecode file
    :param dest_lecode_file: destination of the lecode file
    :param game_track_path: subpath to the track directory
    :param copy_track_paths: where are stored the track to copy
    :param move_track_paths: where are stored the track to move
    :param ctfile_path: where is the ctfile (track and cup definition)
    :param lpar_path: where is the lpar_path (game modification like speed, speedometer, ...)
    """
    if not copy_track_paths: copy_track_paths = []
    if not move_track_paths: move_track_paths = []

    cmd = [
        WLECT_PATH, "patch", lecode_file, "-od", dest_lecode_file, "--track-dir", game_track_path,
        "--le-define", ctfile_path, "--lpar", lpar_path, "--overwrite"
    ]
    for path in copy_track_paths:
        cmd.extend(["--copy-tracks", path])
    for path in move_track_paths:
        cmd.extend(["--move-tracks", path])
    print(cmd)

    subprocess.run(
        cmd,
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=True,
        stdout=subprocess.PIPE,
        timeout=900
    )

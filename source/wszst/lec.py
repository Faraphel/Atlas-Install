import subprocess


def patch(path: str,
          lecode_file: str = f"./tmp/lecode-PAL.bin",
          dest_lecode_file: str = f"./files/rel/lecode-PAL.bin",
          game_track_path: str = "./files/Race/Course/",
          move_track_path: str = "./files/Race/Course/",
          ctfile_path: str = "./tmp/CTFILE.txt",
          lpar_path: str = "./tmp/lpar-default.txt") -> None:
    """
    Patch the file with a lecode file (this is the adding track part)
    :param path: path to the game file
    :param lecode_file: path to the lecode file
    :param dest_lecode_file: destination of the lecode file
    :param game_track_path: subpath to the track directory
    :param move_track_path: where are stored the track to move
    :param ctfile_path: where is the ctfile (track and cup definition)
    :param lpar_path: where is the lpar_path (game modification like speed, speedometer, ...)
    """
    subprocess.run(
        ["./tools/szs/wlect", "patch", lecode_file, "-od", dest_lecode_file, "--track-dir", game_track_path,
         "--move-tracks", move_track_path, "--le-define", ctfile_path, "--lpar", lpar_path, "--overwrite"],
        creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
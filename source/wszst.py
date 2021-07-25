from .definition import *
import subprocess


def sha1(file, autoadd_path: str = "./file/auto-add/") -> str:
    """
    :param autoadd_path: directory where is autoadd directory
    :param file: track file to check sha1
    :return: track's sha1
    """
    return subprocess.run(["./tools/szs/wszst", "SHA1", file, "--autoadd-path", autoadd_path],
                          check=True, creationflags=CREATE_NO_WINDOW,
                          stdout=subprocess.PIPE).stdout.decode().split(" ")[0]


def normalize(src_file: str, dest_dir: str = "./file/Track/", dest_name: str = "%N.szs",
              output_format: str = "szs", autoadd_path: str = "./file/auto-add/") -> None:
    """
    convert a track into an another format
    :param src_file: source file
    :param dest_dir: destination directory
    :param dest_name: destination filename (%N mean same name as src_file)
    :param output_format: format of the destination track
    :param autoadd_path: path of the auto-add directory
    """
    subprocess.run(["./tools/szs/wszst", "NORMALIZE", src_file, "--DEST",
        dest_dir+dest_name, "--"+output_format, "--overwrite", "--autoadd-path",
        autoadd_path], creationflags=CREATE_NO_WINDOW, stderr=subprocess.PIPE)


def wit_extract(file: str, dest_dir: str) -> None:
    """
    extract the game into a directory
    :param file: game's file to extract (can be WBFS, ISO, CISO)
    :param dest_dir: where to extract the game
    """
    subprocess.run(["./tools/wit/wit", "EXTRACT", get_nodir(file), "--DEST", dest_dir],
                    creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))


def create(file: str) -> None:
    """
    convert a directory into a szs file
    :param file: create a .szs file from the directory {file}.d
    """
    subprocess.run(["./tools/szs/wszst", "CREATE", get_nodir(file) + ".d", "-d", get_nodir(file),
                    "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                   check=True, stdout=subprocess.PIPE)


def str_patch(path: str) -> None:
    """
    Patch the main.dol file
    :param path: path to the game
    """
    subprocess.run(["./tools/szs/wstrt", "patch", get_nodir(path) + "/sys/main.dol", "--clean-dol",
                    "--add-lecode"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(path),
                   check=True, stdout=subprocess.PIPE)


def lec_patch(path: str,
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
        ["./tools/szs/wlect", "patch", lecode_file, "-od",
         dest_lecode_file, "--track-dir", game_track_path,
         "--move-tracks", move_track_path, "--le-define", ctfile_path, "--lpar",
         lpar_path, "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=path, check=True, stdout=subprocess.PIPE)


def edit(file: str, region_ID: str = "P", name: str = "Mario Kart Wii") -> None:
    """
    Edit game property like region or name
    :param file: game's file
    :param region_ID: new region_ID
    :param name: new name
    """
    subprocess.run(["./tools/wit/wit", "EDIT", get_nodir(file), "--id",
                    f"RMC{region_ID}60", "--name", name, "--modify", "ALL"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                   check=True, stdout=subprocess.PIPE)


def autoadd(file: str, dest_dir: str) -> None:
    """
    Create an auto_add directory from a game file
    :param file: the game's path
    :param dest_dir: directory where to store autoadd file
    """
    subprocess.run(["./tools/szs/wszst", "AUTOADD", get_nodir(file) + "/files/Race/Course/", "--DEST", dest_dir],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                   check=True, stdout=subprocess.PIPE)


def bmg_encode(file: str) -> None:
    """
    Encode a txt file into a bmg file
    :param file: txt file to convert
    """
    subprocess.run(["./tools/szs/wbmgt", "ENCODE", get_nodir(file), "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))


def bmg_cat(path: str, subfile: str = ".d/message/Common.bmg") -> str:
    """
    read a bmg file
    :param path: path to a szs file
    :param subfile: path to a subdirectory
    :return: bmg definition
    """
    return subprocess.run(["./tools/szs/wbmgt", "CAT", get_nodir(path) + subfile],
                          creationflags=CREATE_NO_WINDOW, cwd=get_dir(path),
                          check=True, stdout=subprocess.PIPE).stdout.decode()


def wit_copy(src_path, dst_path, format: str = "ISO") -> None:
    """
    Copy the game into an another format
    :param src_path: original game path
    :param dst_path: new game path
    :param format: format for the new game
    """
    subprocess.run(["./tools/wit/wit", "COPY", get_nodir(src_path), "--DEST",
                    get_nodir(dst_path), f"--{format.lower()}", "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(dst_path),
                   check=True, stdout=subprocess.PIPE)


def ctc_patch_bmg(bmgs: list, ctfile: str = "./file/CTFILE.txt"):
    """
    Patch a bmg file with a ctfile with OVERWRITE option
    :param bmgs: all bmg files
    :param ctfile: the ctfile path
    :return: combined bmg
    """
    bmg_cmd = []
    for bmg in bmgs: bmg_cmd.extend(["--patch-bmg", f"OVERWRITE={bmg}"])
    return subprocess.run(
            ["tools/szs/wctct", "bmg", "--le-code", "--long", ctfile, *bmg_cmd],
            creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE).stdout.decode()


def img_encode(src_file: str, format: str) -> None:
    """
    Encode an .png image into a new format
    :param src_file: .png image
    :param format: new image format
    """
    subprocess.run(["./tools/szs/wimgt", "ENCODE", src_file, "-x", format, "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)


def szs_extract(file: str, dest_dir: str) -> None:
    """
    Extract an szs in a directory
    :param file: .szs file
    :param dest_dir: directory where to extract the file
    """
    subprocess.run(["./tools/szs/wszst", "EXTRACT", get_nodir(file), "--DEST", dest_dir+".d"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))
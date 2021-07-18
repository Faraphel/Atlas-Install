from .definition import *
import subprocess


def sha1(file):
    """
    :param file: track file to check sha1
    :return: track's sha1
    """
    return subprocess.run(["./tools/szs/wszst", "SHA1", file, "--autoadd-path", "./file/auto-add/"],
                          check=True, creationflags=CREATE_NO_WINDOW,
                          stdout=subprocess.PIPE).stdout.decode().split(" ")[0]


def normalize(src_file: str, dest_dir: str = "./file/Track/", dest_name: str = "%N.szs",
              output_format: str = "szs", autoadd_path: str = "./file/auto-add/", use_popen: bool = False):
    """
    :param use_popen: True if you want to use Popen to convert
    :param src_file: source file
    :param dest_dir: destination directory
    :param dest_name: destination filename (%N mean same name as src_file)
    :param output_format: format of the destination track
    :param autoadd_path: path of the auto-add directory
    :return: 0
    """
    if use_popen: cmd_process = subprocess.Popen
    else: cmd_process = subprocess.run
    return cmd_process([
        "./tools/szs/wszst", "NORMALIZE", src_file, "--DEST",
        dest_dir+dest_name, "--"+output_format, "--overwrite", "--autoadd-path",
        autoadd_path], creationflags=CREATE_NO_WINDOW, stderr=subprocess.PIPE)


def wit_extract(file: str, dest_dir: str):
    """
    :param file: game's file to extract (can be WBFS, ISO, CISO)
    :param dest_dir: where to extract the game
    :return: ?
    """
    subprocess.run(["./tools/wit/wit", "EXTRACT", get_nodir(file), "--DEST", dest_dir],
                    creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))


def create(file: str):
    """
    :param file: create a .szs file from the directory {file}.d
    :return:
    """
    subprocess.run(["./tools/szs/wszst", "CREATE", get_nodir(file) + ".d", "-d", get_nodir(file),
                    "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                   check=True, stdout=subprocess.PIPE)


def str_patch(file: str):
    subprocess.run(["./tools/szs/wstrt", "patch", get_nodir(file) + "/sys/main.dol", "--clean-dol",
                    "--add-lecode"], creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                   check=True, stdout=subprocess.PIPE)


def lec_patch(file: str,
              lecode_file: str = f"./tmp/lecode-PAL.bin",
              dest_lecode_file: str = f"./files/rel/lecode-PAL.bin",
              game_track_path: str = "./files/Race/Course/",
              move_track_path: str = "./files/Race/Course/",
              ctfile_path: str = "./tmp/CTFILE.txt",
              lpar_path: str = "./tmp/lpar-default.txt"):
    subprocess.run(
        ["./tools/szs/wlect", "patch", lecode_file, "-od",
         dest_lecode_file, "--track-dir", game_track_path,
         "--move-tracks", move_track_path, "--le-define", ctfile_path, "--lpar",
         lpar_path, "--overwrite"], creationflags=CREATE_NO_WINDOW, cwd=file, check=True, stdout=subprocess.PIPE)


def edit(file, region_ID: str = "P", name: str = "Mario Kart Wii"):
    subprocess.run(["./tools/wit/wit", "EDIT", get_nodir(file), "--id",
                    f"RMC{region_ID}60", "--name", name, "--modify", "ALL"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                   check=True, stdout=subprocess.PIPE)


def autoadd(file: str, dest_dir: str):
    subprocess.run(["./tools/szs/wszst", "AUTOADD", get_nodir(file) + "/files/Race/Course/", "--DEST", dest_dir],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file),
                   check=True, stdout=subprocess.PIPE)


def bmg_encode(file: str):
    subprocess.run(["./tools/szs/wbmgt", "ENCODE", get_nodir(file), "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))


def bmg_cat(path: str, subfile: str = ".d/message/Common.bmg"):
    return subprocess.run(["./tools/szs/wbmgt", "CAT", get_nodir(path) + subfile],
                          creationflags=CREATE_NO_WINDOW, cwd=get_dir(path),
                          check=True, stdout=subprocess.PIPE).stdout.decode()


def wit_copy(src_path, dst_path, format: str = "ISO"):
    subprocess.run(["./tools/wit/wit", "COPY", get_nodir(src_path), "--DEST",
                    get_nodir(dst_path), f"--{format.lower()}", "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(dst_path),
                   check=True, stdout=subprocess.PIPE)


def ctc_patch_bmg(bmgs: list, ctfile: str = "./file/CTFILE.txt"):
    bmg_cmd = []
    for bmg in bmgs: bmg_cmd.extend(["--patch-bmg", f"OVERWRITE={bmg}"])
    return subprocess.run(
            ["tools/szs/wctct", "bmg", "--le-code", "--long", ctfile, *bmg_cmd],
            creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE).stdout.decode()


def img_encode(src_file, format):
    subprocess.run(["./tools/szs/wimgt", "ENCODE", src_file, "-x", format, "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)


def szs_extract(file, dest_dir):
    subprocess.run(["./tools/szs/wszst", "EXTRACT", get_nodir(file), "--DEST", dest_dir+".d"],
                   creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))
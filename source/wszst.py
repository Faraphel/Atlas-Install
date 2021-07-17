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


def extract(file: str, dest_dir: str):
    subprocess.run(["./tools/wit/wit", "EXTRACT", get_nodir(file), "--DEST", dest_dir],
                    creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))


def create(file: str):
    pass


def wstrt_patch(file: str):
    pass


def wlect_patch(file: str,
                lecode_file: str = f"./files/rel/lecode-PAL.bin",
                game_track_path: str = "./files/Race/Course/",
                move_track_path: str = "./files/Race/Course/",
                ctfile_path: str = "./tmp/CTFILE.txt",
                lpar_path: str = "./tmp/lpar-default.txt"):
    pass

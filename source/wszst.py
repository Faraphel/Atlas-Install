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
              output_format: str = "szs", autoadd_path: str = "./file/auto-add/"):
    """
    :param src_file: source file
    :param dest_dir: destination directory
    :param dest_name: destination filename (%N mean same name as src_file)
    :param output_format: format of the destination track
    :param autoadd_path: path of the auto-add directory
    :return: 0
    """
    subprocess.run([
        "./tools/szs/wszst", "NORMALIZE", src_file, "--DEST",
        dest_dir+dest_name, "--"+output_format, "--overwrite", "--autoadd-path",
        autoadd_path], creationflags=CREATE_NO_WINDOW, stderr=subprocess.PIPE)
    return 0


def extract(file: str, dest_dir: str):
    subprocess.call(["./tools/wit/wit", "EXTRACT", get_nodir(file), "--DEST", dest_dir],
                    creationflags=CREATE_NO_WINDOW, cwd=get_dir(file))
import subprocess
from . import error

WSZST_PATH = "./tools/szs/wszst"


@error.better_wszst_error(wszst_tools=WSZST_PATH)
def extract(file: str, dest_dir: str = None) -> None:
    """
    Extract an szs in a directory
    :param file: .szs file
    :param dest_dir: directory where to extract the file
    """
    if dest_dir is None: dest_dir = file
    subprocess.run([WSZST_PATH, "EXTRACT", file, "--DEST", dest_dir + ".d"],
                   creationflags=subprocess.CREATE_NO_WINDOW)


@error.better_wszst_error(wszst_tools=WSZST_PATH)
def analyze(file: str) -> dict:
    """
    return dictionnary with information about the track
    :param file: track file
    :return: directory
    """
    ana_track = subprocess.run([WSZST_PATH, "ANALYZE", file], check=True,
                               creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE).stdout.decode()

    dict_track = {}
    for line in ana_track.split("\n"):
        if "=" in line:
            key, value = line.split("=", maxsplit=1)
            dict_track[key.strip()] = value.strip()

    return dict_track


@error.better_wszst_error(wszst_tools=WSZST_PATH)
def sha1(file, autoadd_path: str = "./file/auto-add/") -> str:
    """
    :param autoadd_path: directory where is autoadd directory
    :param file: track file to check sha1
    :return: track's sha1
    """
    return subprocess.run([WSZST_PATH, "SHA1", file, "--autoadd-path", autoadd_path],
                          check=True, creationflags=subprocess.CREATE_NO_WINDOW,
                          stdout=subprocess.PIPE).stdout.decode().split(" ")[0]


@error.better_wszst_error(wszst_tools=WSZST_PATH)
def normalize(src_file: str, dest_file: str = "./file/Track/%N.szs",
              output_format: str = "szs", autoadd_path: str = "./file/auto-add/") -> None:
    """
    convert a track into an another format
    :param src_file: source file
    :param dest_file: destination filename (%N mean same name as src_file)
    :param output_format: format of the destination track
    :param autoadd_path: path of the auto-add directory
    """
    subprocess.run([WSZST_PATH, "NORMALIZE", src_file, "--DEST", dest_file, "--" + output_format,
                    "--overwrite", "--autoadd-path", autoadd_path],
                   creationflags=subprocess.CREATE_NO_WINDOW, stderr=subprocess.PIPE)


@error.better_wszst_error(wszst_tools=WSZST_PATH)
def create(file: str) -> None:
    """
    convert a directory into a szs file
    :param file: create a .szs file from the directory {file}.d
    """
    subprocess.run([WSZST_PATH, "CREATE", file + ".d", "-d", file, "--overwrite"],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)


@error.better_wszst_error(wszst_tools=WSZST_PATH)
def autoadd(path: str, dest_dir: str) -> None:
    """
    Create an auto_add directory from a game file
    :param path: the game's path
    :param dest_dir: directory where to store autoadd file
    """
    subprocess.run([WSZST_PATH, "AUTOADD", path + "/files/Race/Course/", "--DEST", dest_dir],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
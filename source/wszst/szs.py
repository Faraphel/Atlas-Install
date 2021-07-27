import subprocess


def extract(file: str, dest_dir: str = None) -> None:
    """
    Extract an szs in a directory
    :param file: .szs file
    :param dest_dir: directory where to extract the file
    """
    if dest_dir is None: dest_dir = file
    subprocess.run(["./tools/szs/wszst", "EXTRACT", file, "--DEST", dest_dir + ".d"],
                   creationflags=subprocess.CREATE_NO_WINDOW)


def sha1(file, autoadd_path: str = "./file/auto-add/") -> str:
    """
    :param autoadd_path: directory where is autoadd directory
    :param file: track file to check sha1
    :return: track's sha1
    """
    return subprocess.run(["./tools/szs/wszst", "SHA1", file, "--autoadd-path", autoadd_path],
                          check=True, creationflags=subprocess.CREATE_NO_WINDOW,
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
    subprocess.run(["./tools/szs/wszst", "NORMALIZE", src_file, "--DEST", dest_dir + dest_name, "--" + output_format,
                    "--overwrite", "--autoadd-path", autoadd_path],
                   creationflags=subprocess.CREATE_NO_WINDOW, stderr=subprocess.PIPE)


def create(file: str) -> None:
    """
    convert a directory into a szs file
    :param file: create a .szs file from the directory {file}.d
    """
    subprocess.run(["./tools/szs/wszst", "CREATE", file + ".d", "-d", file, "--overwrite"],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)


def autoadd(file: str, dest_dir: str) -> None:
    """
    Create an auto_add directory from a game file
    :param file: the game's path
    :param dest_dir: directory where to store autoadd file
    """
    subprocess.run(["./tools/szs/wszst", "AUTOADD", file + "/files/Race/Course/", "--DEST", dest_dir],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)
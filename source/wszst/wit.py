from . import *


def extract(file: str, dest_dir: str) -> None:
    """
    extract the game into a directory
    :param file: game's file to extract (can be WBFS, ISO, CISO)
    :param dest_dir: where to extract the game
    """
    subprocess.run(["./tools/wit/wit", "EXTRACT", file, "--DEST", dest_dir],
                   creationflags=CREATE_NO_WINDOW)


def edit(file: str, region_ID: str = "P", name: str = "Mario Kart Wii") -> None:
    """
    Edit game property like region or name
    :param file: game's file
    :param region_ID: new region_ID
    :param name: new name
    """
    subprocess.run(
        ["./tools/wit/wit", "EDIT", file, "--id", f"RMC{region_ID}60", "--name", name, "--modify", "ALL"],
        creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)


def copy(src_path, dst_path, format: str = "ISO") -> None:
    """
    Copy the game into an another format
    :param src_path: original game path
    :param dst_path: new game path
    :param format: format for the new game
    """
    subprocess.run(["./tools/wit/wit", "COPY", src_path, "--DEST", dst_path, f"--{format.lower()}", "--overwrite"],
                   creationflags=CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)

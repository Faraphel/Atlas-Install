import subprocess
from . import error

WIT_PATH = "./tools/wit/wit"


@error.better_wszst_error(wszst_tools=WIT_PATH)
def extract(file: str, dst_dir: str) -> None:
    """
    extract the game into a directory
    :param file: game's file to extract (can be WBFS, ISO, CISO)
    :param dst_dir: where to extract the game
    """
    subprocess.run([WIT_PATH, "EXTRACT", file, "--DEST", dst_dir],
                   creationflags=subprocess.CREATE_NO_WINDOW)


@error.better_wszst_error(wszst_tools=WIT_PATH)
def edit(file: str, region_ID: str = "P", name: str = "Mario Kart Wii") -> None:
    """
    Edit game property like region or name
    :param file: game's file
    :param region_ID: new region_ID
    :param name: new name
    """
    subprocess.run(
        [WIT_PATH, "EDIT", file, "--id", f"RMC{region_ID}60", "--name", name, "--modify", "ALL"],
        creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)


@error.better_wszst_error(wszst_tools=WIT_PATH)
def copy(src_path: str, dst_path: str, format: str = "ISO") -> None:
    """
    Copy the game into an another format
    :param src_path: original game path
    :param dst_path: new game path
    :param format: format for the new game
    """
    subprocess.run([WIT_PATH, "COPY", src_path, "--DEST", dst_path, f"--{format.lower()}", "--overwrite"],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE)

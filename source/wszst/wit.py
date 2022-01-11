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
def edit(file: str, game_code: str = "RMC", region_ID: str = "P", game_variant: str = "01", name: str = "Mario Kart Wii") -> None:
    """
    Edit game property like region or name
    :param game_variant: for example, the 60 in RMCP60
    :param game_code: code for the game. MKWii is RMC.
    :param file: game's file
    :param region_ID: new region_ID
    :param name: new name
    """
    subprocess.run(
        [WIT_PATH, "EDIT", file, "--id", f"{game_code}{region_ID}{game_variant}", "--name", name, "--modify", "ALL"],
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

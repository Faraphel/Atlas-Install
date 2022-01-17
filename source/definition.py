from threading import Thread
import subprocess
import sys
import os

GITHUB_REPOSITORY = "Faraphel/MKWF-Install"
GITHUB_MASTER_BRANCH = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/master/"
GITHUB_DEV_BRANCH = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/dev/"
ZIPBALL_MASTER_BRANCH = f"https://github.com/{GITHUB_REPOSITORY}/zipball/master/"
ZIPBALL_DEV_BRANCH = f"https://github.com/{GITHUB_REPOSITORY}/zipball/dev/"
VERSION_FILE_URL = GITHUB_MASTER_BRANCH + "version"
GITHUB_HELP_PAGE_URL = f"https://github.com/{GITHUB_REPOSITORY}/wiki/help"
DISCORD_URL = "https://discord.gg/HEYW5v8ZCd"

CHUNK_SIZE: int = 524288  # chunk size used to download file

get_filename = lambda file: ".".join(file.split(".")[:-1])
get_nodir = lambda file: file.replace("\\", "/").split("/")[-1]
get_dir = lambda file: "/".join(file.replace("\\", "/").split("/")[:-1])
get_extension = lambda file: file.split(".")[-1]

bmgID_track_move = {
    "T11": 0x7008, "T12": 0x7001, "T13": 0x7002, "T14": 0x7004,
    "T21": 0x7000, "T22": 0x7005, "T23": 0x7006, "T24": 0x7007,
    "T31": 0x7009, "T32": 0x700f, "T33": 0x700b, "T34": 0x7003,
    "T41": 0x700e, "T42": 0x700a, "T43": 0x700c, "T44": 0x700d,

    "T51": 0x7010, "T52": 0x7014, "T53": 0x7019, "T54": 0x701a,
    "T61": 0x701b, "T62": 0x701f, "T63": 0x7017, "T64": 0x7012,
    "T71": 0x7015, "T72": 0x701e, "T73": 0x701d, "T74": 0x7011,
    "T81": 0x7018, "T82": 0x7016, "T83": 0x7013, "T84": 0x701c,
}


region_id_to_name = {
    "J": "JAP",
    "P": "PAL",
    "K": "KO",
    "E": "USA"
}

gamelang_to_lang = {
    "E": "en",  # english (UK)
    "U": "en",  # english (America)
    "F": "fr",  # french (France)
    "Q": "fr",  # french (Quebec)
    "G": "ge",  # german
    "I": "it",  # italian
    "S": "es",  # spanish (Spain)
    "M": "es",  # spanish (Mexico)

    "J": "en",  # japan - no translation
    "K": "en",  # korean - no translation
}

warning_color = {
    1: "\\\\c{YOR4}",
    2: "\\\\c{YOR6}",
    3: "\\\\c{BLUE}",
}

get_version_from_string = lambda v: list(map(int, v.split('.')))


def restart():
    """
    restart the application
    """
    subprocess.Popen([sys.executable] + sys.argv, creationflags=subprocess.CREATE_NO_WINDOW, cwd=os.getcwd())
    exit()


def in_thread(func):
    """
    instead of calling a function, this will start it in a thread
    :param func: function to thread
    :return: threaded function
    """

    def wrapped_func(*args, **kwargs) -> Thread:
        """
        function that will be returned instead of the function, will call it in a thread
        :param args: args of the original function
        :param kwargs: kwargs of the original function
        :return: thread object to the function
        """
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()
        return thread

    return wrapped_func


def get_next_available_dir(parent_dir: str, dir_name: str) -> str:
    """
    get the next available directory name
    :param parent_dir: name of the parent directory
    :param dir_name: wished name for the directory
    :return: name of the directory with a potential index at the end
    """
    i = 1
    final_dir_name = dir_name
    while True:
        path_dir = os.path.realpath(parent_dir + "/" + final_dir_name)
        if not os.path.exists(path_dir): return path_dir
        final_dir_name = f"{dir_name} ({i})"
        i += 1


def str_to_int(string: str) -> int:
    base: int = 10
    if string.startswith("0x"): base = 16
    return int(string, base=base)

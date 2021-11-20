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

EMPTY_TRACK = '  T T44; T44; 0x00; "_"; ""; "-"\n'

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

trackname_color = {
    "MSRDS": "\\\\c{green}MSRDS\\\\c{off}",
    "CTR": "\\\\c{YOR4}CTR\\\\c{off}",
    "CTTR": "\\\\c{YOR5}CTTR\\\\c{off}",
    "CNR": "\\\\c{YOR5}CNR\\\\c{off}",
    "DKR": "\\\\c{YOR6}DKR\\\\c{off}",
    "LCP": "\\\\c{green}LCP\\\\c{off}",
    "LEGO-R": "\\\\c{red2}LEGO-R\\\\c{off}",
    "MP9": "\\\\c{YOR0}MP9\\\\c{off}",
    "MSUSA": "\\\\c{green}MSUSA\\\\c{off}",
    "FZMV": "\\\\c{YOR2}FZMV\\\\c{off}",
    "KAR": "\\\\c{green}KAR\\\\c{off}",
    "KO": "\\\\c{YOR5}KO\\\\c{off}",
    "FZ": "\\\\c{YOR2}FZ\\\\c{off}",
    "RV": "\\\\c{white}RV\\\\c{off}",
    "SADX": "\\\\c{blue2}SADX\\\\c{off}",
    "SCR": "\\\\c{YOR2}SCR\\\\c{off}",
    "SH": "\\\\c{red}SH\\\\c{off}",
    "SM64": "\\\\c{red1}SM64\\\\c{off}",
    "SMB1": "\\\\c{red2}SMB1\\\\c{off}",
    "SMB2": "\\\\c{red3}SMB2\\\\c{off}",
    "SSBB": "\\\\c{red4}SSBB\\\\c{off}",
    "SMS": "\\\\c{YOR6}SMS\\\\c{off}",
    "SMO": "\\\\c{YOR7}SMO\\\\c{off}",
    "VVVVVV": "\\\\c{blue}VVVVVV\\\\c{off}",
    "WF": "\\\\c{green}WF\\\\c{off}",
    "WP": "\\\\c{yellow}WP\\\\c{off}",
    "Zelda OoT": "\\\\c{green}Zelda OoT\\\\c{off}",
    "Zelda TP": "\\\\c{green}Zelda TP\\\\c{off}",
    "Zelda WW": "\\\\c{green}Zelda WW\\\\c{off}",
    "PMWR": "\\\\c{yellow}PMWR\\\\c{off}",
    "SHR": "\\\\c{green}SHR\\\\c{off}",
    "SK64": "\\\\c{green}SK64\\\\c{off}",
    "SMG": "\\\\c{red2}SMG\\\\c{off}",
    "Spyro 1": "\\\\c{blue}Spyro 1\\\\c{off}",

    "Wii U": "\\\\c{red4}Wii U\\\\c{off}",
    "Wii": "\\\\c{blue}Wii\\\\c{off}",

    "3DS": "\\\\c{YOR3}3DS\\\\c{off}",
    "DS": "\\\\c{white}DS\\\\c{off}",
    "GCN": "\\\\c{blue2}GCN\\\\c{off}",
    "GBA": "\\\\c{blue1}GBA\\\\c{off}",
    "N64": "\\\\c{red}N64\\\\c{off}",
    "SNES": "\\\\c{green}SNES\\\\c{off}",
    "RMX": "\\\\c{YOR4}RMX\\\\c{off}",
    "MKT": "\\\\c{YOR5}MKT\\\\c{off}",
    "GP": "\\\\c{YOR6}GP\\\\c{off}",

    "Boost": "\\\\c{YOR3}Boost\\\\c{off}",
}

region_id_to_name = {
    "J": "JAP",
    "P": "PAL",
    "K": "KO",
    "E": "USA"
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
        if not os.path.exists(path_dir): break
        final_dir_name = f"{dir_name} ({i})"
        i += 1

    return parent_dir + "/" + final_dir_name

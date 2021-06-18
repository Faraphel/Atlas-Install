get_filename = lambda file: ".".join(file.split(".")[:-1])
get_nodir = lambda file: file.replace("\\", "/").split("/")[-1]
get_dir = lambda file: "/".join(file.replace("\\", "/").split("/")[:-1])
get_extension = lambda file: file.split(".")[-1]
get_track_wu8 = lambda track: f"./file/Track-WU8/{track}.wu8"
get_track_szs = lambda track: f"./file/Track/{track}.szs"


def get_trackname(name=None, prefix=None, suffix=None, track=None):
    if track:
        name = track["name"]
        if "prefix" in track: prefix = track["prefix"]
        if "suffix" in track: suffix = track["suffix"]
    if prefix: name = prefix + " " + name
    if suffix: name = name + " (" + suffix + ")"
    return name


CREATE_NO_WINDOW = 0x08000000
VERSION = "0.8.1"


def filecopy(src, dst):
    with open(src, "rb") as f1:
        with open(dst, "wb") as f2:
            f2.write(f1.read())  # could be buffered

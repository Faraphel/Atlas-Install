get_filename = lambda file: ".".join(file.split(".")[:-1])
get_nodir = lambda file: file.split("/")[-1].split("\\")[-1]
get_extension = lambda file: file.split(".")[-1]

CREATE_NO_WINDOW = 0x08000000
VERSION = "0.7"

def filecopy(src, dst):
    with open(src, "rb") as f1:
        with open(dst, "wb") as f2:
            f2.write(f1.read()) # could be buffered
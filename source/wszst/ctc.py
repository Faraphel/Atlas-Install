import subprocess


def ctc_patch_bmg(bmgs: list, ctfile: str = "./file/CTFILE.txt"):
    """
    Patch a bmg file with a ctfile with OVERWRITE option
    :param bmgs: all bmg files
    :param ctfile: the ctfile path
    :return: combined bmg
    """
    bmg_cmd = []
    for bmg in bmgs: bmg_cmd.extend(["--patch-bmg", f"OVERWRITE={bmg}"])
    return subprocess.run(
        ["tools/szs/wctct", "bmg", "--le-code", "--long", ctfile, *bmg_cmd],
        creationflags=subprocess.CREATE_NO_WINDOW, check=True, stdout=subprocess.PIPE).stdout.decode()
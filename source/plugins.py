from pathlib import Path


def initialise() -> None:
    """
    Execute all the scripts in the ./plugins/ directory that don't start with an underscore.
    :return:
    """
    for file in Path("./plugins/").rglob("[!_]*.py"):
        exec(file.read_text(encoding="utf8"), globals())

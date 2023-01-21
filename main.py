import argparse

from source.option import Options
from source.translation import load_language


options = Options.from_file("./option.json")
translater = load_language(options.language.get())
window = None


def main_gui():
    global window

    from source.interface.gui import install
    window = install.Window(options)
    window.run()


def main_cli(argparser: argparse.ArgumentParser):
    from source.interface.cli import install
    install.cli(options, argparser)


argparser = argparse.ArgumentParser()
argparser.add_argument(
    "-i", "--interface",
    choices=["gui", "cli"],
    default="gui",
    help="should the installer be started with a graphical interface or with the command line interface"
)
args, _ = argparser.parse_known_args()

match args.interface:
    case "gui": main_gui()
    case "cli": main_cli(argparser)

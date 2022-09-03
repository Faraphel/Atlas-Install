import argparse

from source.option import Options
from source.translation import load_language


# this allows every variable to be accessible from other files, useful for the plugins
self = __import__(__name__)

options = Options.from_file("./option.json")
translater = load_language(options.language.get())


def main_gui():
    from source.interface.gui import install
    self.window = install.Window(options)
    self.window.run()


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

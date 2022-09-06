import argparse
import sys
from pathlib import Path

from source.interface import is_valid_source_path, is_valid_destination_path, get_finished_installation_message
from source.mkw.Game import Game
from source.mkw.ModConfig import ModConfig
from source.mkw.collection.Extension import Extension
from source.translation import translate as _


def cli(options, argparser: argparse.ArgumentParser):
    argparser.add_argument("-m", "--mod", required=True, help="name of the mod to install")
    argparser.add_argument("-s", "--source", required=True, help="path to the original game")
    argparser.add_argument("-d", "--dest", required=True, help="destination directory of the patched game")
    argparser.add_argument("-ot", "--output_type", required=True, help="format of the patched game")
    args = argparser.parse_args()

    mod_config_path = Path(f"./Pack/{args.mod}/mod_config.json")
    if not mod_config_path.exists():
        print(_("ERROR_INVALID_MOD") % args.mod, file=sys.stderr)
        return
    mod_config = ModConfig.from_file(mod_config_path)

    game_path = Path(args.source)
    if not is_valid_source_path(game_path):
        print(_("ERROR_INVALID_SOURCE_GAME") % game_path, file=sys.stderr)
        return
    game = Game(args.source)

    destination_path = Path(args.dest)
    if not is_valid_destination_path(destination_path):
        print(_("ERROR_INVALID_GAME_DESTINATION") % destination_path, file=sys.stderr)
        return

    try: output_type = Extension[args.output_type]
    except KeyError:
        print(_("ERROR_INVALID_OUTPUT_TYPE") % args.output_type, file=sys.stderr)
        return

    # installation and progress bar
    progressbar_max: int = 40

    title: str = ""
    description: str = ""
    current_part: int = 0
    max_part: int = 0
    current_step: int = 0
    max_step: int = 0
    determinate: bool = False

    for step in game.install_mod(
        dest=destination_path,
        mod_config=mod_config,
        output_type=output_type,
        options=options
    ):
        if step.title is not None: title = step.title
        if step.description is not None: description = step.description
        if step.max_part is not None: max_part = step.max_part
        if step.set_part is not None: current_part = step.set_part
        if step.part is not None: current_part += step.part
        if step.max_step is not None: max_step = step.max_step
        if step.set_step is not None: current_step = step.set_step
        if step.step is not None: current_step += step.step
        if step.determinate is not None: determinate = step.determinate

        progressbar_step: int = current_step * progressbar_max // max_step if max_step > 0 else 0

        print(
            "\033[H\033[J", "\n",  # clear the shell
            title, f"({current_part} / {max_part})", "\n",  # print the title and the actual part
            description, "\n",  # print the description
            *((
                f"{round((current_step / max_step if max_step > 0 else 0) * 100, 2)}% "
                f"[{'#' * progressbar_step}{' ' * (progressbar_max - progressbar_step)}]"
            ) if determinate else ()),  # if determinate, show a progress bar

            sep=""
        )

    print(
        "\033[H\033[J",
        get_finished_installation_message(mod_config),

        sep="\n"
    )

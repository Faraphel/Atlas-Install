from pathlib import Path

from source.mkw.Game import Game
from source.mkw.ModConfig import ModConfig
from source.translation import translate as _
from source.mkw.collection.Extension import Extension


def cli(options):
    print(_("TITLE_INSTALL"))

    packs = []
    for pack in Path("./Pack/").iterdir():
        packs.append(pack)

    mod_name = input(_("TEXT_INPUT_MOD_NAME") % [pack.name for pack in packs])
    mod_config = ModConfig.from_file(Path(f"./Pack/{mod_name}/mod_config.json"))

    source_path = input(_("TEXT_INPUT_SOURCE_PATH"))
    game = Game(source_path)

    destination_directory = input(_("TEXT_INPUT_DESTINATION_DIRECTORY"))
    destination_path = Path(destination_directory)

    output_name = input(_("TEXT_INPUT_OUPUT_TYPE") % [extension.name for extension in Extension])
    output_type = Extension[output_name]

    progressbar_max: int = 30

    title: str = ""
    description: str = ""
    current_part: int = 0
    max_part: int = 0
    current_step: int = 0
    max_step: int = 0

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

        progressbar_step: int = current_step * progressbar_max // max_step if max_step > 0 else 0

        print("\033[H\033[J", end="")
        print(title, f"({current_part} / {max_part})")
        print(description)
        print(
            f"{round((current_step / max_step if max_step > 0 else 0) * 100, 2)}% "
            f"[{'#' * progressbar_step}{' ' * (progressbar_max - progressbar_step)}]"
        )


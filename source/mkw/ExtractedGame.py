from pathlib import Path
from typing import Generator

from source.mkw.ModConfig import ModConfig
from source.wt import szs
import json


class ExtractedGame:
    """
    Class that represents an extracted game
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def extract_autoadd(self, destination_path: Path | str) -> Generator[dict, None, None]:
        """
        Extract all the autoadd files from the game to destination_path
        :param destination_path: directory where the autoadd files will be extracted
        :return: directory where the autoadd files were extracted
        """
        yield {"description": "Extracting autoadd files...", "determinate": False}
        szs.autoadd(self.path / "files/Race/Course/", destination_path)

    def install_mystuff(self) -> Generator[dict, None, None]:
        """
        Install mystuff directory
        :return:
        """
        yield {"description": "Installing MyStuff directory...", "determinate": False}
        ...

    def install_file(self, mod_config: ModConfig, patch_directory: Path | str, subfile: Path | str) \
            -> Generator[dict, None, None]:
        """
        Install a file into the game
        :param patch_directory: patch_directory where the subfile is located
        :param subfile: subfile to install
        :param mod_config: the mod to install
        """
        subfile = Path(subfile)
        yield {"description": f"Patch {patch_directory.name}\nInstalling {subfile.name}...", "determinate": False}

        '''
        configuration = {
            "base": "/files/test.json",  # path a another json file to use as a base

            "mode": "copy",  # copy, replace, ignore, edit the subfile [default: copy]
            # if edit is set, use the file in the extracted game as a source
            # replace can't be used inside szs

            "replace_regex": None,  # regex expression to match the file on the game to replace
            "if": "True",  # safe eval expression to check if the file should be installed

            "operation": {  # other operation for the file
                "img-generate": {
                    # width, height, default color, ... can be determined from the base file
                    "format": "RGB",  # type of the image
                    "layers": [
                        {"type": "image", ...},
                        {"type": "text", ...}
                    ]
                }

                "tpl-encode": {"encoding": "TPL.RGB565"},  # encode an image to a tpl with the given format

                "bmg-replace": {
                    "mode": "regex"  # regex or id
                    "template": {
                        "CWF": "{{ ONLINE_SERVICE }}",  # regex type expression
                        "0x203F": "{{ ONLINE_SERVICE }}"  # id type expression
                    }
                }
            }
        }
        '''

        configuration = {  # default configuration
            "mode": "copy",
            "if": "True",
        }
        configuration_path = subfile.with_suffix(subfile.suffix + ".json")
        if configuration_path.exists(): configuration |= json.loads(configuration_path.read_text(encoding="utf8"))

    def install_patch(self, mod_config: ModConfig, patch_directory: Path | str) -> Generator[dict, None, None]:
        """
        Install a patch into the game
        :param mod_config: the mod to install
        :param patch_directory: directory containing the patch
        """
        patch_directory = Path(patch_directory)
        yield {"description": f"Installing Patch {patch_directory.parent.name}...", "determinate": False}

        for subfile in filter(lambda sf: sf.suffix == ".json", patch_directory.glob("*")):
            self.install_file(mod_config, patch_directory, subfile)

    def install_all_patch(self, mod_config: ModConfig) -> Generator[dict, None, None]:
        """
        Install all patchs of the mod_config into the game
        :param mod_config: the mod to install
        :return:
        """
        yield {"description": "Installing all Patch...", "determinate": False}

        # for all directory that are in the root of the mod, and don't start with an underscore,
        # for all the subdirectory named "_PATCH", apply the patch
        for part_directory in mod_config.get_mod_directory().glob("[!_]*"):
            for patch_directory in part_directory.glob("_PATCH/"):
                self.install_patch(mod_config, patch_directory)

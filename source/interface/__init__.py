import os
from pathlib import Path
from typing import TYPE_CHECKING

from source import system
from source.translation import translate_external, translate as _

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig


def is_valid_source_path(path: Path):
    """
    :param path: path to the source path
    :return: is the source path valid
    """
    return path.exists() and str(path) != "."


def is_valid_destination_path(path: Path):
    """
    :param path: path to the destination path
    :return: is the destination path valid
    """
    return path.exists() and str(path) != "."


def is_user_root():
    """
    :return: does the user have root permission (linux only)
    """
    return system != "lin64" or os.getuid() == 0


def are_permissions_enabled():
    """
    :return: does the installer have writing and execution permissions
    """
    return os.access("./", os.W_OK | os.X_OK)


def get_finished_installation_message(mod_config: "ModConfig") -> str:
    message: str = translate_external(
        mod_config, mod_config.messages.get("installation_completed", {}).get("text", {})
    )

    return f"{_('TEXT_INSTALLATION_FINISHED_SUCCESSFULLY')}" + (
        f"\n{_('TEXT_MESSAGE_FROM_AUTHOR')} :\n\n{message}" if message != "" else ""
    )
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class PathOutsidePatch(Exception):
    def __init__(self, forbidden_path: Path, allowed_range: Path):
        super().__init__(f"Error : path {forbidden_path} outside of allowed range {allowed_range}")


class InvalidPatchMode(Exception):
    def __init__(self, mode: str):
        super().__init__(f"Error : mode \"{mode}\" is not implemented")

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source.mkw.Patch import Patch
    from source.mkw.Patch.PatchObject import PatchObject


class PathOutsidePatch(Exception):
    def __init__(self, forbidden_path: Path, allowed_range: Path):
        super().__init__(f'Error : path "{forbidden_path}" outside of allowed range {allowed_range}')


class InvalidPatchMode(Exception):
    def __init__(self, patch: "PatchObject", mode: str):
        super().__init__(f'Error : mode "{mode}" is not implemented (in patch : "{patch.full_path}")')


class InvalidSourceMode(Exception):
    def __init__(self, patch: "PatchObject", source: str):
        super().__init__(f'Error : source "{source}" is not implemented (in patch : "{patch.full_path}")')

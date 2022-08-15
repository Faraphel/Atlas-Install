from pathlib import Path
from typing import TYPE_CHECKING
from source.translation import translate as _

if TYPE_CHECKING:
    from source.mkw.Patch import Patch
    from source.mkw.Patch.PatchObject import PatchObject


class PathOutsidePatch(Exception):
    def __init__(self, forbidden_path: Path, allowed_range: Path):
        super().__init__(_("PATH", ' "', forbidden_path, '" ', "OUTSIDE_ALLOWED_RANGE", ' "', {allowed_range}, '" '))


class InvalidPatchMode(Exception):
    def __init__(self, patch: "PatchObject", mode: str):
        super().__init__(_("MODE", ' "', mode, '" ', "IS_NOT_IMPLEMENTED",
                           "(", "IN_PATCH", ' : "', patch.full_path, '")'))


class InvalidSourceMode(Exception):
    def __init__(self, patch: "PatchObject", source: str):
        super().__init__(_("SOURCE", ' "', source, '" ', "IS_NOT_IMPLEMENTED",
                           "(", "IN_PATCH", ' : "', patch.full_path, '")'))

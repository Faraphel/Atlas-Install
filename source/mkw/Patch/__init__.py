from typing import TYPE_CHECKING
from source.translation import translate as _

if TYPE_CHECKING:
    from source.mkw.Patch import Patch
    from source.mkw.Patch.PatchObject import PatchObject


class InvalidPatchMode(Exception):
    def __init__(self, patch: "PatchObject", mode: str):
        super().__init__(_("ERROR_PATCH_MODE_NOT_IMPLEMENTED") % (mode, patch.full_path))


class InvalidSourceMode(Exception):
    def __init__(self, patch: "PatchObject", source: str):
        super().__init__(_("ERROR_SOURCE_NOT_IMPLEMENTED") % (source, patch.full_path))

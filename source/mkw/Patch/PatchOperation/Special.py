from typing import IO, TYPE_CHECKING

from source.mkw.Patch.PatchOperation import AbstractPatchOperation

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class Special(AbstractPatchOperation):
    """
    use a file defined as special in the patch to replace the current file content
    """

    type = "special"

    def __init__(self, name: str):
        self.name = name

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        patch_content = patch.special_file[self.name]
        patch_content.seek(0)
        return file_name, patch_content

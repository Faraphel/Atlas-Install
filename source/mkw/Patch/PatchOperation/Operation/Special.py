from typing import IO

from source.mkw.Patch.PatchOperation.Operation import *


Patch: any


class Special(AbstractOperation):
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

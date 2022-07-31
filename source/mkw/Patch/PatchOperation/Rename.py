from typing import IO

from source.mkw.Patch.PatchOperation import AbstractPatchOperation


Patch: any


class Rename(AbstractPatchOperation):
    """
    Rename the output file
    """

    type = "rename"

    def __init__(self, name: str):
        self.name = name

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        return self.name, file_content

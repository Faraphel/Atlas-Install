from io import BytesIO
from typing import IO

from source.mkw.Patch.PatchOperation import AbstractPatchOperation
from source.wt import bmg


Patch: any


class BmgDecoder(AbstractPatchOperation):
    """
    decode a bmg file to a txt file
    """

    type = "bmg-decode"

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        """
        Patch a file to decode it to a txt file
        :param patch: the patch that is applied
        :param file_name: the file_name of the file
        :param file_content: the content of the file
        :return: the new name and new content of the file
        """
        patch_content = BytesIO(bmg.decode_data(file_content.read()).encode("utf-8"))
        return f"{file_name}.txt", patch_content

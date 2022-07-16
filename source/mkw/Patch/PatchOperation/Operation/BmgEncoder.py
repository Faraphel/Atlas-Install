from io import BytesIO
from typing import IO

from source.mkw.Patch.PatchOperation.Operation import *
from source.wt import bmg

Patch: any


class BmgEncoder(AbstractOperation):
    """
    encode a bmg file to a txt file
    """

    type = "bmg-encode"

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        """
        Patch a file to encode it to a bmg file
        :param patch: the patch that is applied
        :param file_name: the file_name of the file
        :param file_content: the content of the file
        :return: the new name and new content of the file
        """
        patched_file_name = file_name.rsplit(".", 1)[0]
        patch_content = BytesIO(bmg.encode_data(file_content.read().decode("utf-8")))
        return patched_file_name, patch_content

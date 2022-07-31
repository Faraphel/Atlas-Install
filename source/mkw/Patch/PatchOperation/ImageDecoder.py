from io import BytesIO
from typing import IO

from source.mkw.Patch.PatchOperation import AbstractPatchOperation
from source.wt import img


Patch: any


class ImageDecoder(AbstractPatchOperation):
    """
    decode a game image to a image file
    """

    type = "img-decode"

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        """
        Patch a file to encode it in a game image file
        :param patch: the patch that is applied
        :param file_name: the file_name of the file
        :param file_content: the content of the file
        :return: the new name and new content of the file
        """
        patch_content = BytesIO(img.decode_data(file_content.read()))
        return f"{file_name}.png", patch_content

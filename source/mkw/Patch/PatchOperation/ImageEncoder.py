from io import BytesIO
from typing import IO

from source.mkw.Patch.PatchOperation import AbstractPatchOperation
from source.wt import img


Patch: any


class ImageEncoder(AbstractPatchOperation):
    """
    encode an image to a game image file
    """

    type = "img-encode"

    def __init__(self, encoding: str = "CMPR"):
        """
        :param encoding: compression of the image
        """
        self.encoding: str = encoding

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        """
        Patch a file to encode it in a game image file
        :param patch: the patch that is applied
        :param file_name: the file_name of the file
        :param file_content: the content of the file
        :return: the new name and new content of the file
        """
        # remove the last extension of the filename
        patched_file_name = file_name.rsplit(".", 1)[0]
        patch_content = BytesIO(img.encode_data(file_content.read(), self.encoding))

        return patched_file_name, patch_content

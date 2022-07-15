from abc import ABC, abstractmethod
from typing import IO

Patch: any
Layer: any


class AbstractOperation(ABC):

    mode: str  # name of the operation

    @abstractmethod
    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        """
        patch a file and return the new file_path (if changed) and the new content of the file
        """


from source.mkw.Patch.PatchOperation.Operation import ImageDecoder, ImageEncoder, Rename, Special, StrEditor, \
    BmgEditor, ImageEditor
__all__ = ["AbstractOperation", "ImageDecoder", "ImageEncoder", "Rename",
           "Special", "StrEditor", "BmgEditor", "ImageEditor"]
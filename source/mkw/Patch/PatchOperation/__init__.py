from abc import ABC, abstractmethod
from typing import IO, Type, TYPE_CHECKING

from source.translation import translate as _

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class InvalidPatchOperation(Exception):
    def __init__(self, operation: str):
        super().__init__(_("ERROR_OPERATION_NOT_IMPLEMENTED") % operation)


class AbstractPatchOperation(ABC):
    """
    An AbstractPatchOperation representing any PatchOperation that can be used on one of the game files
    """

    mode: str  # name of the operation

    @abstractmethod
    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        """
        patch a file and return the new file_path (if changed) and the new content of the file
        """

    @classmethod
    def get(cls, name: str) -> Type["AbstractPatchOperation"]:
        """
        Return an operation from its name
        :name: name of the operation
        :return: an Operation from its name
        """

        for subclass in filter(lambda subclass: subclass.type == name, cls.__subclasses__()):
            return subclass
        raise InvalidPatchOperation(name)


#  load all the subclass of AbstractPatchOperation to that __subclasses__ can filter them
from source.mkw.Patch.PatchOperation import (
    ImageDecoder, ImageEncoder, Rename, Special, StrEditor,
    BmgTxtEditor, ImageEditor, BmgEncoder, BmgDecoder, SzsEditor
)

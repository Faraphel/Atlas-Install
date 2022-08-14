from io import BytesIO
from typing import IO, TYPE_CHECKING
from abc import ABC, abstractmethod

from source.mkw.Patch.PatchOperation import AbstractPatchOperation

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class InvalidBmgLayerMode(Exception):
    def __init__(self, layer_mode: str):
        super().__init__(f"Error : bmg layer mode \"{layer_mode}\" is not implemented")


class AbstractLayer(ABC):
    """
    Represent a Layer for a bmgtxt patch
    """

    @abstractmethod
    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        """
        Patch a bmg with the actual layer. Return the new bmg content.
        """
        ...

    @classmethod
    def get(cls, layer: dict) -> "AbstractLayer":
        """
        return the correct type of layer corresponding to the layer mode
        :param layer: the layer to load
        """
        for subclass in filter(lambda subclass: subclass.mode == layer["mode"], cls.__subclasses__()):
            layer.pop("mode")
            return subclass(**layer)
        raise InvalidBmgLayerMode(layer["mode"])


class BmgTxtEditor(AbstractPatchOperation):
    """
    edit a decoded bmg
    """

    type = "bmgtxt-edit"

    def __init__(self, layers: list[dict]):
        """
        :param layers: layers
        """
        self.layers = layers

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        decoded_content: str = file_content.read().decode("utf-8")

        for layer in self.layers:
            decoded_content = AbstractLayer.get(layer).patch_bmg(patch, decoded_content)

        patch_content: IO = BytesIO(decoded_content.encode("utf-8"))
        return file_name, patch_content


# Load the subclasses so that get_layer can filter them.
from source.mkw.Patch.PatchOperation.BmgTxtEditor import (
    CTFileLayer, FormatOriginalTrackLayer, IDLayer, PatchLayer, RegexLayer
)
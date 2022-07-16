from io import BytesIO
from typing import IO

from source.mkw.Patch import *
from source.mkw.Patch.PatchOperation.Operation import *
from source.mkw.Patch.PatchOperation.Operation.BmgTxtEditor.Layer import *


class BmgTxtEditor(AbstractOperation):
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
            decoded_content = self.Layer(layer).patch_bmg(patch, decoded_content)

        patch_content: IO = BytesIO(decoded_content.encode("utf-8"))
        return file_name, patch_content

    class Layer:
        """
        represent a layer for a bmg-edit
        """

        def __new__(cls, layer: dict) -> "Layer":
            """
            return the correct type of layer corresponding to the layer mode
            :param layer: the layer to load
            """
            for subclass in filter(lambda subclass: subclass.mode == layer["mode"],
                                   AbstractLayer.__subclasses__()):
                layer.pop("mode")
                return subclass(**layer)
            raise InvalidBmgLayerMode(layer["mode"])

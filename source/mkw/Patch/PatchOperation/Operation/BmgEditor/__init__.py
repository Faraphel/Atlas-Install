from io import BytesIO
from typing import IO

from source.mkw.Patch import *
from source.mkw.Patch.PatchOperation.Operation import *
from source.mkw.Patch.PatchOperation.Operation.BmgEditor.Layer import *
from source.wt import bmg


class BmgEditor(AbstractOperation):
    """
    edit a bmg
    """

    type = "bmg-edit"

    def __init__(self, layers: list[dict]):
        """
        :param layers: layers
        """
        self.layers = layers

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        decoded_content = bmg.decode_data(file_content.read())

        for layer in self.layers:
            decoded_content = self.Layer(layer).patch_bmg(patch, decoded_content)

        patch_content = BytesIO(bmg.encode_data(decoded_content))
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
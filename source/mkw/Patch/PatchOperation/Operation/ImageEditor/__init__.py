from io import BytesIO
from typing import IO

from PIL import Image

from source.mkw.Patch import *
from source.mkw.Patch.PatchOperation.Operation import *
from source.mkw.Patch.PatchOperation.Operation.ImageEditor.Layer import *


class ImageGenerator(AbstractOperation):
    """
    generate a new image based on a file and apply a generator on it
    """

    type = "img-edit"

    def __init__(self, layers: list[dict]):
        self.layers: list["Layer"] = [self.Layer(layer) for layer in layers]

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        image = Image.open(file_content).convert("RGBA")

        for layer in self.layers:
            image = layer.patch_image(patch, image)

        patch_content = BytesIO()
        image.save(patch_content, format="PNG")
        patch_content.seek(0)

        return file_name, patch_content

    class Layer:
        """
        represent a layer for an image generator
        """

        def __new__(cls, layer: dict) -> "Layer":
            """
            return the correct type of layer corresponding to the layer mode
            :param layer: the layer to load
            """
            for subclass in filter(lambda subclass: subclass.type == layer["type"],
                                   AbstractLayer.__subclasses__()):
                layer.pop("type")
                return subclass(**layer)
            raise InvalidImageLayerType(layer["type"])

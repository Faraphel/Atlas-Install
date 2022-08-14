from io import BytesIO
from typing import IO, TYPE_CHECKING
from abc import abstractmethod, ABC
from PIL import Image

from source.mkw.Patch.PatchOperation import AbstractPatchOperation

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class InvalidImageLayerType(Exception):
    def __init__(self, layer_type: str):
        super().__init__(f"Error : image layer type \"{layer_type}\" is not implemented")


class AbstractLayer(ABC):
    x: int
    y: int
    x1: int
    x2: int
    y1: int
    y2: int
    font_size: int

    def get_bbox(self, image: Image.Image) -> tuple:
        """
        return a tuple of a bbox from x1, x2, y1, y2
        if float, calculate the position like a percentage on the image
        if int, use directly the position
        """
        if isinstance(x1 := self.x1, float): x1 = int(x1 * image.width)
        if isinstance(y1 := self.y1, float): y1 = int(y1 * image.height)
        if isinstance(x2 := self.x2, float): x2 = int(x2 * image.width)
        if isinstance(y2 := self.y2, float): y2 = int(y2 * image.height)

        return x1, y1, x2, y2

    def get_bbox_size(self, image: Image.Image) -> tuple:
        """
        return the size that a layer use on the image
        """
        x1, y1, x2, y2 = self.get_bbox(image)
        return x2 - x1, y2 - y1

    def get_font_size(self, image: Image.Image) -> int:
        """
        return the font_size of a layer
        """
        return int(self.font_size * image.height) if isinstance(self.font_size, float) else self.font_size

    def get_layer_position(self, image: Image.Image) -> tuple:
        """
        return a tuple of the x and y position
        if x / y is a float, calculate the position like a percentage on the image
        if x / y is an int, use directly the position
        """
        if isinstance(x := self.x, float): x = int(x * image.width)
        if isinstance(y := self.y, float): y = int(y * image.height)

        return x, y

    @abstractmethod
    def patch_image(self, patch: "Patch", image: Image.Image) -> Image.Image:
        """
        Patch an image with the actual layer. Return the new image.
        """
        ...

    @classmethod
    def get(cls, layer: dict) -> "AbstractLayer":
        """
        return the correct type of layer corresponding to the layer mode
        :param layer: the layer to load
        """
        for subclass in filter(lambda subclass: subclass.type == layer["type"], cls.__subclasses__()):
            layer.pop("type")
            return subclass(**layer)
        raise InvalidImageLayerType(layer["type"])


class ImageGenerator(AbstractPatchOperation):
    """
    generate a new image based on a file and apply a generator on it
    """

    type = "img-edit"

    def __init__(self, layers: list[dict]):
        self.layers: list["AbstractLayer"] = [AbstractLayer.get(layer) for layer in layers]

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        image = Image.open(file_content).convert("RGBA")

        for layer in self.layers:
            image = layer.patch_image(patch, image)

        patch_content = BytesIO()
        image.save(patch_content, format="PNG")
        patch_content.seek(0)

        return file_name, patch_content


# Load the class so that __subclasses__ can find them
from source.mkw.Patch.PatchOperation.ImageEditor import (
    ColorLayer, ImageLayer, TextLayer
)

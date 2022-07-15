from abc import abstractmethod, ABC

from PIL import Image


Patch: any


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


from source.mkw.Patch.PatchOperation.Operation.ImageEditor.Layer import ColorLayer, ImageLayer, TextLayer
__all__ = ["AbstractLayer", "ColorLayer", "ImageLayer", "TextLayer"]

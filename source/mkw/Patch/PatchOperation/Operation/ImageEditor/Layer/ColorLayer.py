from PIL import ImageDraw, Image

from source.mkw.Patch.PatchOperation.Operation.ImageEditor.Layer import *


class ColorLayer(AbstractLayer):
    """
    Represent a layer that fill a rectangle with a certain color on the image
    """
    type = "color"

    def __init__(self, color: tuple[int] = (0,), x1: int | float = 0, y1: int | float = 0,
                 x2: int | float = 1.0, y2: int | float = 1.0):
        self.x1: int | float = x1
        self.y1: int | float = y1
        self.x2: int | float = x2
        self.y2: int | float = y2
        self.color: tuple[int] = tuple(color)

    def patch_image(self, patch: "Patch", image: Image.Image):
        draw = ImageDraw.Draw(image)
        draw.rectangle(self.get_bbox(image), fill=self.color)

        return image
from typing import TYPE_CHECKING

from PIL import Image

from source.mkw import PathOutsideAllowedRange
from source.mkw.Patch.PatchOperation.ImageEditor import AbstractLayer

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class ImageLayer(AbstractLayer):
    """
    Represent a layer that paste an image on the image
    """
    type = "image"

    def __init__(self, image_path: str, x1: int | float = 0, y1: int | float = 0,
                 x2: int | float = 1.0, y2: int | float = 1.0):
        self.x1: int | float = x1
        self.y1: int | float = y1
        self.x2: int | float = x2
        self.y2: int | float = y2
        self.image_path: str = image_path

    def patch_image(self, patch: "Patch", image: Image.Image) -> Image.Image:
        # check if the path is outside of the allowed directory
        layer_image_path = patch.path / self.image_path
        if not layer_image_path.is_relative_to(patch.path):
            raise PathOutsideAllowedRange(layer_image_path, patch.path)

        # load the image that will be pasted
        layer_image = Image.open(layer_image_path.resolve()) \
            .resize(self.get_bbox_size(image)) \
            .convert("RGBA")

        # paste onto the final image the layer with transparency support
        image.alpha_composite(
            layer_image,
            dest=self.get_bbox(image)[:2],
        )

        return image


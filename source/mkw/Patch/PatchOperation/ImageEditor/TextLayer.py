from pathlib import Path
from typing import TYPE_CHECKING

from PIL import ImageFont, ImageDraw, Image

from source.mkw.Patch import PathOutsidePatch
from source.mkw.Patch.PatchOperation.ImageEditor import AbstractLayer

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class TextLayer(AbstractLayer):
    """
    Represent a layer that write a text on the image
    """
    type = "text"

    def __init__(self, text: str, font_path: str | None = None, font_size: int = 10,
                 color: tuple[int] = (255,),
                 x: int | float = 0, y: int | float = 0):
        self.x: int = x
        self.y: int = y
        self.font_path: str | None = font_path
        self.font_size: int = font_size
        self.color: tuple[int] = tuple(color)
        self.text: str = text

    def patch_image(self, patch: "Patch", image: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(image)

        if self.font_path is not None:
            font_image_path = patch.path / self.font_path
            if not font_image_path.is_relative_to(patch.path):
                raise PathOutsidePatch(font_image_path, patch.path)
        else:
            font_image_path = None

        font = ImageFont.truetype(
            font=str(font_image_path.resolve())
            if isinstance(font_image_path, Path) else
            font_image_path,
            size=self.get_font_size(image)
        )
        draw.text(
            self.get_layer_position(image),
            text=patch.mod_config.multiple_safe_eval(self.text),
            fill=self.color,
            font=font
        )

        return image

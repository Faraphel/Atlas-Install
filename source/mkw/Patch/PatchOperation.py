from abc import ABC, abstractmethod
from io import BytesIO
from typing import IO

from PIL import Image, ImageDraw, ImageFont

from source.mkw.Patch import *


class PatchOperation:
    """
    Represent an operation that can be applied onto a patch to modify it before installing
    """
    class Operation(ABC):
        @abstractmethod
        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
            """
            patch a file and return the new file_path (if changed) and the new content of the file
            """

        def __new__(cls, name) -> "Operation":
            """
            Return an operation from its name
            :return: an Operation from its name
            """
            for subclass in filter(lambda subclass: subclass.type == name, cls.__subclasses__()):
                return subclass
            raise InvalidPatchOperation(name)

    class ImageGenerator(Operation):
        """
        generate a new image based on a file and apply a generator on it
        """

        type = "img-generate"

        def __init__(self, layers: list[dict]):
            self.layers: list["Layer"] = [self.Layer(layer) for layer in layers]

        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
            image = Image.open(file_content)

            for layer in self.layers:
                image = layer.patch_image(patch, image)

            patch_content = BytesIO()
            image.save(patch_content, format="PNG")
            patch_content.seek(0)

            return file_name, patch_content

        class Layer(ABC):
            """
            represent a layer for a image generator
            """

            def __new__(cls, layer: dict) -> "Layer":
                """
                return the correct type of layer corresponding to the layer mode
                :param layer: the layer to load
                """
                for subclass in filter(lambda subclass: subclass.type == layer["type"], cls.__subclasses__()):
                    layer.pop("type")
                    return subclass(**layer)
                raise InvalidImageLayerType(layer["type"])

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

        class ColorLayer(Layer):
            """
            Represent a layer that fill a rectangle with a certain color on the image
            """
            type = "color"

            def __init__(self, color: tuple[int] = (0,), x1: int | float = 0, y1: int | float = 0, x2: int | float = 1,
                         y2: int | float = 1):
                self.x1: int = x1
                self.y1: int = y1
                self.x2: int = x2
                self.y2: int = y2
                self.color: tuple[int] = tuple(color)

            def patch_image(self, patch: "Patch", image: Image.Image):
                draw = ImageDraw.Draw(image)
                draw.rectangle(self.get_bbox(image), self.color)

                return image

        class ImageLayer(Layer):
            """
            Represent a layer that paste an image on the image
            """
            type = "image"

            def __init__(self, image_path: str, x1: int | float = 0, y1: int | float = 0, x2: int | float = 1,
                         y2: int | float = 1):
                self.x1: int = x1
                self.y1: int = y1
                self.x2: int = x2
                self.y2: int = y2
                self.image_path: str = image_path

            def patch_image(self, patch: "Patch", image: Image.Image) -> Image.Image:
                # check if the path is outside of the allowed directory
                layer_image_path = patch.path / self.image_path
                if not layer_image_path.is_relative_to(patch.path): raise PathOutsidePatch(layer_image_path, patch.path)

                layer_image = Image.open(layer_image_path).resize(self.get_bbox_size(image)).convert("RGBA")

                image.paste(
                    layer_image,
                    box=self.get_bbox(image),
                    mask=layer_image
                )

                return image

        class TextLayer(Layer):
            """
            Represent a layer that write a text on the image
            """
            type = "text"

            def __init__(self, text: str, font_path: str | None = None, font_size: int = 10, color: tuple[int] = (255,),
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

                font = ImageFont.truetype(font=font_image_path, size=self.get_font_size(image))
                draw.text(self.get_layer_position(image), text=self.text, fill=self.color, font=font)

                return image

    class TplConverter(Operation):
        """
        convert an image to a tpl file
        """

        type = "tpl-encode"

        def __init__(self, *args, **kwargs):
            print(args, kwargs)

        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
            return file_name, file_content

    class BmgEditor(Operation):
        """
        edit a bmg
        """

        type = "bmg-replace"

        def __init__(self, *args, **kwargs):
            print(args, kwargs)

        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
            return file_name, file_content

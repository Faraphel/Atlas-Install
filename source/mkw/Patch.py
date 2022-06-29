from pathlib import Path
import json
from PIL import Image, ImageDraw

from abc import abstractmethod, ABC
from typing import Generator, IO
from io import BytesIO

from source.safe_eval import safe_eval


class PathOutsidePatch(Exception):
    def __init__(self, forbidden_path: Path, allowed_range: Path):
        super().__init__(f"Error : path {forbidden_path} outside of allowed range {allowed_range}")


class InvalidPatchMode(Exception):
    def __init__(self, mode: str):
        super().__init__(f"Error : mode \"{mode}\" is not implemented")


class InvalidPatchOperation(Exception):
    def __init__(self, operation: str):
        super().__init__(f"Error : operation \"{operation}\" is not implemented")


class InvalidImageLayerType(Exception):
    def __init__(self, layer_type: str):
        super().__init__(f"Error : layer type \"{layer_type}\" is not implemented")


class Patch:
    """
    Represent a patch object
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path}>"

    def safe_eval(self, template: str, extracted_game: "ExtractedGame") -> str:
        """
        Safe eval with a patch environment
        :param extracted_game: the extracted game to patch
        :param template: template to evaluate
        :return: the result of the evaluation
        """
        return safe_eval(
            template,
            extra_token_map={"extracted_game": "extracted_game"},
            env={"extracted_game": extracted_game},
        )

    def install(self, extracted_game: "ExtractedGame") -> Generator[dict, None, None]:
        """
        patch a game with this Patch
        """
        # take all the files in the root directory, and patch them into the game.
        # Patch is not directly applied to the root to avoid custom configuration
        # on the base directory.
        for file in self.path.iterdir():
            pathname = file.relative_to(self.path)
            yield from PatchDirectory(self, str(pathname)).install(extracted_game, extracted_game.path / pathname)


class PatchOperation:
    """
    Represent an operation that can be applied onto a patch to modify it before installing
    """

    @classmethod
    def get_operation_by_name(cls, name: str):
        match name:
            case "img-generate":
                return cls.ImageGenerator
            case "tpl-encode":
                return cls.TplConverter
            case "bmg-replace":
                return cls.BmgEditor
            case _:
                raise InvalidPatchOperation(name)

    class Operation(ABC):
        @abstractmethod
        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
            """
            patch a file and return the new file_path (if changed) and the new content of the file
            """

    class ImageGenerator(Operation):
        """
        generate a new image based on a file and apply a generator on it
        """

        def __init__(self, layers: list[dict]):
            self.layers: list["Layer"] = [self.Layer(layer) for layer in layers]

        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
            image = Image.open(file_content)

            for layer in self.layers:
                image = layer.patch_image(patch, image)

            patch_content = BytesIO()
            image.save(patch_content, format="PNG")
            patch_content.seek(0)

            return file_name, file_content

        class Layer(ABC):
            """
            represent a layer for a image generator
            """

            def __new__(cls, layer: dict):
                match layer["type"]:
                    case "color":
                        obj = ColorLayer
                    case "image":
                        obj = ImageLayer
                    case "text":
                        obj = TextLayer
                    case _:
                        raise InvalidImageLayerType(layer["type"])

                return obj(**layer)

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

            def __init__(self, image_path: str, x1: int | float = 0, y1: int | float = 0, x2: int | float = 1,
                         y2: int | float = 1):
                self.x1: int = x1
                self.y1: int = y1
                self.x2: int = x2
                self.y2: int = y2
                self.image_path: str = image_path

            def patch(self, patch: "Patch", image: Image.Image) -> Image.Image:
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

        class TextLayer:
            """
            Represent a layer that write a text on the image
            """

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
                draw.text(self.get_layer_position(layer), text=self.text, fill=self.color, font=font)

                return image

    class TplConverter(Operation):
        """
        convert an image to a tpl file
        """

        def __init__(self): ...

        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO): ...

    class BmgEditor(Operation):
        """
        edit a bmg
        """

        def __init__(self): ...

        def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO): ...


class PatchObject:
    """
    Represent an object inside a patch
    """

    def __init__(self, patch: Patch, subpath: str):
        self.patch = patch
        self.subpath = subpath
        self._configuration = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_path}>"

    @property
    def full_path(self) -> Path:
        return self.patch.path / self.subpath

    @property
    def configuration(self) -> dict:
        """
        return the configuration from the file
        """
        if self._configuration is not None: return self._configuration

        # default configuration
        self._configuration = {
            "mode": "copy",
            "if": "True",
        }

        configuration_path = self.full_path.with_suffix(self.full_path.suffix + ".json")
        if not configuration_path.exists(): return self._configuration

        self._configuration |= json.loads(configuration_path.read_text(encoding="utf8"))

        # if configuration inherit from an another file, then load it from the patch root,
        # keep this configuration keys over inherited one.
        # pop "base" to avoid infinite loop
        while "base" in self._configuration:
            self._configuration |= json.loads(
                (self.patch.path / self._configuration.pop("base")).read_text(encoding="utf8"))

        return self._configuration

    def subfile_from_path(self, path: Path) -> "PatchObject":
        """
        return a PatchObject from a path
        """
        obj = PatchDirectory if path.is_dir() else PatchFile
        return obj(self.patch, str(path.relative_to(self.patch.path)))

    @abstractmethod
    def install(self, extracted_game: "ExtractedGame", game_subpath: Path) -> Generator[dict, None, None]:
        """
        install the PatchObject into the game
        yield the step of the process
        """


class PatchFile(PatchObject):
    """
    Represent a file from a patch
    """

    def get_source_path(self, game_subpath: Path):
        """
        Return the path of the file that the patch is applied on.
        If the configuration mode is set to "edit", then return the path of the file inside the Game
        Else, return the path of the file inside the Patch
        """
        match self.configuration["mode"]:
            case "edit":
                return game_subpath
            case _:
                return self.full_path

    def install(self, extracted_game: "ExtractedGame", game_subpath: Path) -> Generator[dict, None, None]:
        """
        patch a subfile of the game with the PatchFile
        """
        yield {"description": f"Patching {self}"}

        if self.full_path.name.startswith("#"):
            print(f"special file : {self} [install to {game_subpath}]")
            return

        if self.patch.safe_eval(self.configuration["if"], extracted_game) == "False": return

        # apply operation on the file
        patch_source: Path = self.get_source_path(game_subpath)
        patch_name: str = game_subpath.name
        patch_content: IO = open(patch_source, "rb")

        for operation_name, operation in self.configuration.get("operation", {}).items():
            # process every operation and get the new patch_path (if the name is changed)
            # and the new content of the patch
            patch_name, patch_content = PatchOperation.get_operation_by_name(operation_name)(*operation).patch(
                self.patch, patch_name, patch_content
            )

        match self.configuration["mode"]:
            # if the mode is copy, replace the subfile in the game by the PatchFile
            case "copy" | "edit":
                print(f"[copy] copying {self} to {game_subpath}")

                with open(game_subpath.parent / patch_name, "wb") as file:
                    file.write(patch_content.read())

            # if the mode is match, replace all the subfiles that match match_regex by the PatchFile
            case "match":
                for game_subfile in game_subpath.parent.glob(self.configuration["match_regex"]):
                    # disallow patching files outside of the game
                    if not game_subfile.relative_to(extracted_game.path):
                        raise PathOutsidePatch(game_subfile, extracted_game.path)
                    # patch the game with the subpatch
                    print(f"[match] copying {self} to {game_subfile}")

                    with open(game_subfile.parent / patch_name, "wb") as file:
                        file.write(patch_content.read())

            # else raise an error
            case _:
                raise InvalidPatchMode(self.configuration["mode"])

        patch_content.close()


class PatchDirectory(PatchObject):
    """
    Represent a directory from a patch
    """

    @property
    def subpatchs(self) -> Generator["PatchObject", None, None]:
        """
        return all the subpatchs inside the PatchDirectory
        """
        for subpath in self.full_path.iterdir():
            if subpath.suffix == ".json": continue
            yield self.subfile_from_path(subpath)

    def install(self, extracted_game: "ExtractedGame", game_subpath: Path) -> Generator[dict, None, None]:
        """
        patch a subdirectory of the game with the PatchDirectory
        """
        yield {"description": f"Patching {self}"}

        if self.patch.safe_eval(self.configuration["if"], extracted_game) == "False": return

        match self.configuration["mode"]:
            # if the mode is copy, then simply patch the subfile into the game with the same path
            case "copy":
                for subpatch in self.subpatchs:
                    # install the subfile in the directory with the same name as the PatchDirectory
                    yield from subpatch.install(extracted_game, game_subpath / subpatch.full_path.name)

            # if the mode is replace, patch all the files that match the replace_regex
            case "match":
                for subpatch in self.subpatchs:
                    # install the subfile in all the directory that match the match_regex of the configuration
                    for game_subfile in game_subpath.parent.glob(self.configuration["match_regex"]):
                        # disallow patching files outside of the game
                        if not game_subfile.relative_to(extracted_game.path):
                            raise PathOutsidePatch(game_subfile, extracted_game.path)
                        # patch the game with the subpatch
                        yield from subpatch.install(extracted_game, game_subfile / subpatch.full_path.name)

            # else raise an error
            case _:
                raise InvalidPatchMode(self.configuration["mode"])


# TODO : extract SZS
# TODO : implement TPL
# TODO : implement BMG


configuration_example = {
    "operation": {  # other operation for the file
        "tpl-encode": {"encoding": "TPL.RGB565"},  # encode an image to a tpl with the given format

        "bmg-replace": {
            "mode": "regex",  # regex or id
            "template": {
                "CWF": "{{ ONLINE_SERVICE }}",  # regex type expression
                "0x203F": "{{ ONLINE_SERVICE }}"  # id type expression
            }
        }
    }
}

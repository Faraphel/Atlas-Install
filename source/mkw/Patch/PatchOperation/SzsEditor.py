from io import BytesIO
from typing import IO, TYPE_CHECKING

from source.mkw.Patch.PatchOperation import AbstractPatchOperation
from source.wt import szs

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class SzsEditor(AbstractPatchOperation):
    """
    patch a track szs file
    """

    type = "szs-edit"

    def __init__(self, scale: dict[str, int] = None, shift: dict[str, int] = None, rotation: dict[str, int] = None,
                 translate: dict[str, int] = None, speed: str = None, laps: str = None):
        self.scale = scale  # example : {"x": 1, "y": 1, "z": 1}
        self.shift = shift
        self.rotation = rotation
        self.translate = translate

        self.speed = float(speed)
        self.laps = int(laps)

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        patched_content = BytesIO(szs.patch(
            file_content.read(),
            scale=self.scale,
            shift=self.shift,
            rotation=self.rotation,
            translate=self.translate,
            speed=self.speed,
            laps=self.laps,
        ))

        return file_name, patched_content

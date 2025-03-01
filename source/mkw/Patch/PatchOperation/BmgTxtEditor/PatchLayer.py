from typing import TYPE_CHECKING

from source.mkw.Patch.PatchOperation.BmgTxtEditor import AbstractLayer
from source.wt import bmg

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class PatchLayer(AbstractLayer):
    """
    Represent a layer that patch a bmg
    """

    mode = "patch"

    def __init__(self, patchs: list[str]):
        self.patchs = patchs

    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        return bmg.cat_data(decoded_content, patchs=self.patchs)

from abc import ABC, abstractmethod

Patch: any


class AbstractLayer(ABC):
    @abstractmethod
    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        """
        Patch a bmg with the actual layer. Return the new bmg content.
        """


from source.mkw.Patch.PatchOperation.Operation.BmgTxtEditor.Layer import IDLayer, RegexLayer, CTFileLayer
__all__ = ["AbstractLayer", "IDLayer", "RegexLayer", "CTFileLayer"]

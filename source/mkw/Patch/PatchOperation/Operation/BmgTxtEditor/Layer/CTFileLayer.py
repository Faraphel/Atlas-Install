from source.mkw.Patch.PatchOperation.Operation.BmgTxtEditor.Layer import *
from source.wt import ctc

Patch: any


class CTFileLayer(AbstractLayer):
    """
    Represent a layer that replace bmg entry by their ID
    """

    mode = "ctfile"

    def __init__(self, template: dict[str, str]):
        self.template = template

    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        return decoded_content + "\n" + (
            ctc.bmg_ctfile(patch.mod_config.get_ctfile(template=self.template))
        ) + "\n"
        # add new bmg definition at the end of the bmg file, overwritting old id.

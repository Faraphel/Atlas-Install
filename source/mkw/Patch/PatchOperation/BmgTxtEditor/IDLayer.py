from typing import TYPE_CHECKING

from source.mkw.Patch.PatchOperation.BmgTxtEditor import AbstractLayer

if TYPE_CHECKING:
    from source.mkw.Patch import Patch


class IDLayer(AbstractLayer):
    """
    Represent a layer that replace bmg entry by their ID
    """

    mode = "id"

    def __init__(self, template: dict[str, str]):
        self.template = template

    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        return decoded_content + "\n" + ("\n".join(
            [f"  {id}\t= {patch.mod_config.multiple_safe_eval(repl)}" for id, repl in self.template.items()]
        )) + "\n"
        # add new bmg definition at the end of the bmg file, overwritting old id.

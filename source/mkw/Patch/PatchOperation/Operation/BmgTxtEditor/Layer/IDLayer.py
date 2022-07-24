from source.mkw.Patch.PatchOperation.Operation.BmgTxtEditor.Layer import *


Patch: any


class IDLayer(AbstractLayer):
    """
    Represent a layer that replace bmg entry by their ID
    """

    mode = "id"

    def __init__(self, template: dict[str, str]):
        self.template = template

    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        return decoded_content + "\n" + ("\n".join(
            [f"  {id}\t= {patch.mod_config.safe_eval(repl, multiple=True)}" for id, repl in self.template.items()]
        )) + "\n"
        # add new bmg definition at the end of the bmg file, overwritting old id.

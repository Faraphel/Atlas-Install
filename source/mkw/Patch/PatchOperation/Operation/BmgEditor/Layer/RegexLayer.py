import re

from source.mkw.Patch.PatchOperation.Operation.BmgEditor.Layer import *


Patch: any


class RegexLayer(AbstractLayer):
    """
    Represent a layer that replace bmg entry by matching them with a regex
    """

    mode = "regex"

    def __init__(self, template: dict[str, str]):
        self.template = template

    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        # TODO : use regex in a better way to optimise speed

        new_bmg_lines: list[str] = []
        for line in decoded_content.split("\n"):
            if (match := re.match(r"^ {2}(?P<id>.*?)\t= (?P<value>.*)$", line, re.DOTALL)) is None:
                # check if the line match a bmg definition, else ignore
                # bmg definition is : 2 spaces, a bmg id, a tab, an equal sign, a space and the bmg text
                continue

            new_bmg_id: str = match.group("id")
            new_bmg_def: str = match.group("value")
            for pattern, repl in self.template.items():
                new_bmg_def = re.sub(
                    pattern,
                    patch.safe_eval(repl, multiple=True),
                    new_bmg_def,
                    flags=re.DOTALL
                )
                # match a pattern from the template, and replace it with its repl

            new_bmg_lines.append(f"  {new_bmg_id}\t={new_bmg_def}")

        return decoded_content + "\n" + ("\n".join(new_bmg_lines)) + "\n"
        # add every new line to the end of the decoded_bmg, old bmg_id will be overwritten.

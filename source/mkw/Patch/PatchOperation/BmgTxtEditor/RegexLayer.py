import re

from source.mkw.Patch.PatchOperation.BmgTxtEditor import AbstractLayer


Patch: any


class RegexLayer(AbstractLayer):
    """
    Represent a layer that replace bmg entry by matching them with a regex
    """

    mode = "regex"

    def __init__(self, template: dict[str, str]):
        self.template = template

    def patch_bmg(self, patch: "Patch", decoded_content: str) -> str:
        def replacement(match: re.Match) -> str:
            """
            Get the replacement for the bmg line
            :param match: the matched bmg line
            :return: the patched bmg line
            """
            id: str = match.group("id")
            value: str = match.group("value")
            for pattern, repl in self.template.items():
                value = re.sub(
                    pattern,
                    patch.mod_config.multiple_safe_eval(repl),
                    value,
                    flags=re.DOTALL
                )

            return f"  {id}\t={value}"

        return re.sub(r" {2}(?P<id>.*?)\t= (?P<value>.*)", replacement, decoded_content)


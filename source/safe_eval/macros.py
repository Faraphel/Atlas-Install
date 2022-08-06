import re


MACRO_START, MACRO_END = "##", "##"


class NotImplementedMacro(Exception):
    def __init__(self, macro: str):
        super().__init__(f"Invalid macro while parsing macros:\n{macro}")


def replace_macro(template: str, macros: dict[str, str]) -> str:
    """
    Replace all the macro defined in macro by their respective value
    :param template: template where to replace the macro
    :param macros: dictionary associating macro with their replacement
    :return: the template with macro replaced
    """

    def format_macro(match: re.Match) -> str:
        if (macro := macros.get(match.group(1).strip())) is None: raise NotImplementedMacro(macro)
        return macro

    # match everything between MACRO_START and MACRO_END.
    return re.sub(rf"{MACRO_START}(.*?){MACRO_END}", format_macro, template)

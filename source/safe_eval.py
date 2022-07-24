import re
from typing import Callable

common_token_map = {  # these operators and function are considered safe to use in the template
   operator: operator
   for operator in
   [">=", "<=", "<<", ">>", "+", "-", "*", "/", "%", "**", ",", "(", ")", "[", "]", "==", "!=", "in", ">", "<",
    "and", "or", "&", "|", "^", "~", ":", "isinstance", "issubclass", "not", "is", "if", "else", "abs", "int",
    "bin", "hex", "oct", "chr", "ord", "len", "str", "bool", "float", "round", "min", "max", "sum", "zip",
    "any", "all", "reversed", "enumerate", "list", "sorted", "hasattr", "for", "range", "type", "repr", "None",
    "True", "False", "getattr"
    ]
} | {  # these methods are considered safe, except for the magic methods
   f".{method}": f".{method}"
   for method in dir(str) + dir(list) + dir(int) + dir(float)
   if not method.startswith("__")
}

TOKEN_START, TOKEN_END = "{{", "}}"
MACRO_START, MACRO_END = "##", "##"


class TemplateParsingError(Exception):
    def __init__(self, token: str):
        super().__init__(f"Invalid token while parsing safe_eval:\n{token}")


class NotImplementedMacro(Exception):
    def __init__(self, macro: str):
        super().__init__(f"Invalid macro while parsing macros:\n{macro}")


class SafeFunction:
    @classmethod
    def get_all_safe_methods(cls) -> dict[str, Callable]:
        """
        get all the safe methods defined by the class
        :return: all the safe methods defined by the class
        """
        return {
            method: getattr(cls, method)
            for method in dir(cls)
            if not method.startswith("__") and method not in ["get_all_safe_methods"]
        }

    @staticmethod
    def getattr(obj: any, attr: str, default: any = None) -> any:
        """
        Safe getattr, raise an error if the attribute is a function
        :param obj: object to get the attribute from
        :param attr: attribute name
        :param default: default value if the attribute is not found
        :return: the attribute value
        """
        attr = getattr(obj, attr) if default is None else getattr(obj, attr, default)
        if callable(attr): raise AttributeError(f"getattr can't be used for functions (tried: {attr})")
        return attr


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


def safe_eval(template: str, env: dict[str, any] = None, macros: dict[str, str] = None) -> str:
    """
    Evaluate the template and return the result in a safe way
    :param env: variables to use when using eval
    :param template: template to evaluate
    :param macros: additionnal macro to replace in the template
    """
    if env is None: env = {}
    if macros is None: macros = {}

    template = replace_macro(template, macros)
    token_map: dict[str, str] = common_token_map | {var: var for var in env}
    final_token: str = ""

    def matched(match: re.Match | str | None, value: str = None) -> bool:
        """
        check if token is matched, if yes, add it to the final token and remove it from the processing token
        :param match: match object
        :param value: if the match is a string, the value to replace the text with
        :return: True if matched, False otherwise
        """
        nonlocal final_token, template

        # if there is no match or the string is empty, return False
        if not match: return False

        if isinstance(match, re.Match):
            template_raw = template[match.end():]
            value = match.group()

        else:
            if not template.startswith(match): return False
            template_raw = template[len(match):]

        template = template_raw.lstrip()
        final_token += value + (len(template_raw) - len(template)) * " "
        return True

    while template:  # while there is still tokens to process
        # if the section is a string, add it to the final token
        # example : "hello", "hello \" world"
        if matched(re.match(r'^(["\'])((\\{2})*|(.*?[^\\](\\{2})*))\1', template)):
            continue

        # if the section is a float or an int, add it to the final token
        # example : 102, 102.59
        if matched(re.match(r'^[0-9]+(?:\.[0-9]+)?', template)):
            continue

        # if the section is a variable, operator or function, replace it by its value
        # example : track.special, +
        for key, value in token_map.items():
            if matched(key, value): break

        # else, the token is invalid, so raise an error
        else:
            raise TemplateParsingError(template)

    # if final_token is set, eval final_token and return the result
    if final_token: return str(eval(final_token, SafeFunction.get_all_safe_methods(), env))
    else: return final_token


def multiple_safe_eval(template: str, env: dict[str, any] = None, macros: dict[str, str] = None) -> str:
    def format_part_template(match: re.Match) -> str:
        """
        when a token is found, replace it by the corresponding value
        :param match: match in the format
        :return: corresponding value
        """
        # get the token string without the brackets, then strip it. Also double antislash
        part_template = match.group(1).strip().replace("\\", "\\\\")
        return safe_eval(part_template, env, macros)

    # pass everything between TOKEN_START and TOKEN_END in the function
    return re.sub(rf"{TOKEN_START}(.*?){TOKEN_END}", format_part_template, template)


import re
from typing import Callable

common_token_map = {  # these operators and function are considered safe to use in the template
   operator: operator
   for operator in
   ["+", "-", "*", "/", "%", "**", ",", "(", ")", "[", "]", "==", "!=", "in", ">", "<", ">=", "<=", "and", "or", "&",
    "|", "^", "~", "<<", ">>", ":", "not", "is", "if", "else", "abs", "int", "bin", "hex", "oct", "chr", "ord", "len",
    "str", "bool", "float", "round", "min", "max", "sum", "zip", "any", "all", "issubclass", "reversed", "enumerate",
    "list", "sorted", "hasattr", "for", "range", "type", "isinstance", "repr", "None", "True", "False", "getattr"
    ]
} | {  # these methods are considered safe, except for the magic methods
   f".{method}": f".{method}"
   for method in dir(str) + dir(list) + dir(int) + dir(float)
   if not method.startswith("__")
}


class TemplateParsingError(Exception):
    def __init__(self, token: str):
        super().__init__(f"Invalid token while parsing track representation:\n{token}")


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


def safe_eval(template: str, extra_token_map: dict[str, str] = None, env: dict[str, any] = None) -> str:
    """
    Evaluate the template and return the result in a safe way
    :param extra_token_map: additionnal tokens to use in the template
    :param env: variables to use when using eval
    :param template: template to evaluate
    """
    if extra_token_map is None: extra_token_map = {}
    if env is None: env = {}

    token_map: dict[str, str] = common_token_map | extra_token_map
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

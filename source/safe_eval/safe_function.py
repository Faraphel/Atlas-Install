
from typing import Callable, Generator


# TODO: exception class


def get_all_safe_functions() -> Generator[list[Callable], None, None]:
    """
    Return all the safe function defined in safe_function
    """
    for obj_name in filter(lambda obj_name: "__" not in obj_name, dir(safe_function)):
        obj = getattr(safe_function, obj_name)
        if callable(obj): yield obj

    yield from safe_builtins


# these functions are builtins function that don't need additional check to be safe
safe_builtins: list[Callable] = [
    abs, all, any, ascii, bin, bool, chr, dict, enumerate, float, hasattr, hex, int,
    isinstance, issubclass, len, list, max, min, oct, ord, range, repr, reversed,
    round, sorted, str, sum, tuple, type, zip,
]


class safe_function:
    """
    Safer version of some python builtins function
    """

    @staticmethod
    def getattr(obj: any, name: str, default=None) -> any:
        """
        Same as normal getattr, but magic attribute are banned
        """
        if "__" in name: raise Exception(f'Magic method are not allowed : "{name}"')
        return getattr(obj, name, default)

    @staticmethod
    def type(obj: any):
        """
        Same as normal type, but the syntax with 3 arguments (to create new type) is banned
        """
        return type(obj)

    @staticmethod
    def eval(template: str, env: dict | None = None):
        """
        Allow a recursive safe_eval, but without the lambda functionality
        """
        from source.safe_eval import safe_eval
        return safe_eval(template, env)

from typing import Callable
from source.translation import translate as _


class BetterSafeEvalError(Exception):
    def __init__(self, template: str):
        super().__init__(_("ERROR_SAFEEVAL") % template)


def better_safe_eval_error(func: Callable, template: str):
    def wrapped(*args, **kwargs):
        try: return func(*args, **kwargs)
        except Exception as exc: raise BetterSafeEvalError(template) from exc

    return wrapped

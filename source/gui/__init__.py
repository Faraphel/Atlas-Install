import traceback
from tkinter import messagebox
from typing import Callable

from source.translation import translate as _


def better_gui_error(func: Callable) -> Callable:
    """
    Decorator to handle GUI errors.
    """

    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except: messagebox.showerror(_("ERROR"), traceback.format_exc())

    return wrapper
import traceback
from pathlib import Path
from tkinter import messagebox
from typing import Callable
from source.translation import translate as _
from source import __version__
import time


def better_gui_error(func: Callable) -> Callable:
    """
    Decorator to handle GUI errors.
    """

    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except Exception:
            exc = traceback.format_exc()
            with Path("error.log").open("a", encoding="utf8") as log_file:
                log_file.write(
                    f"{'#' * 20}\n"
                    f"{time.strftime('%Y/%M/%d %H:%m:%S')}\n"
                    f"Version: {__version__}\n"
                    f"\n"
                    f"{exc}\n"
                    f"\n"
                )
            messagebox.showerror(_("Error"), exc)

    return wrapper

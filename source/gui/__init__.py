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

            exc_split = exc.splitlines()
            if len(exc_split) > 10:
                # if the traceback is too long, only keep the 5 first and 5 last lines of the traceback
                exc_split = exc_split[:5] + ["..."] + exc_split[-5:] + ["", "", _("MORE_IN_ERROR_LOG")]

            messagebox.showerror(_("Error"), "\n".join(exc_split))

    return wrapper

from typing import TYPE_CHECKING
from source.translation import translate as _

if TYPE_CHECKING:
    from pathlib import Path

Tag = str


class PathOutsideAllowedRange(Exception):
    def __init__(self, forbidden_path: "Path", allowed_range: "Path"):
        super().__init__(_("ERROR_PATH_OUTSIDE_RANGE") % (forbidden_path, allowed_range))
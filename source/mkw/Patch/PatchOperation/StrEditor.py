from io import BytesIO
from pathlib import Path
from typing import IO, TYPE_CHECKING

from source.mkw import PathOutsideAllowedRange
from source.mkw.Patch.PatchOperation import AbstractPatchOperation
from source.wt import wstrt

if TYPE_CHECKING:
    from source.mkw.Patch import Patch
    from source import TemplateMultipleSafeEval


class StrEditor(AbstractPatchOperation):
    """
    patch the main.dol file
    """

    type = "str-edit"

    def __init__(self, region: "TemplateMultipleSafeEval" = None, https: "TemplateMultipleSafeEval" = None,
                 domain: "TemplateMultipleSafeEval" = None, sections: list[str] = None):
        self.region = region
        self.https = https
        self.domain = domain
        self.sections = sections

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        checked_sections: list[Path] = []

        for section in self.sections if self.sections is not None else []:
            section_path = patch.path / section
            if not section_path.is_relative_to(patch.path):
                raise PathOutsideAllowedRange(section_path, patch.path)

            checked_sections.append(section_path)
        # for every file in the sections, check if they are inside the patch.

        patch_content = BytesIO(
            wstrt.patch_data(
                file_content.read(),
                region=patch.mod_config.multiple_safe_eval(self.region)() if self.region is not None else None,
                https=patch.mod_config.multiple_safe_eval(self.https)() if self.https is not None else None,
                domain=patch.mod_config.multiple_safe_eval(self.domain)() if self.domain is not None else None,
                sections=checked_sections
            )
        )

        return file_name, patch_content

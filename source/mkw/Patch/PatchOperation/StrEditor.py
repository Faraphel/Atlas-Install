from io import BytesIO
from typing import IO

from source.mkw.Patch.PatchOperation import AbstractPatchOperation
from source.mkw.Patch import *
from source.wt import wstrt


class StrEditor(AbstractPatchOperation):
    """
    patch the main.dol file
    """

    type = "str-edit"

    def __init__(self, region: int = None, https: str = None, domain: str = None, sections: list[str] = None):
        self.region = region
        self.https = https
        self.domain = domain
        self.sections = sections

    def patch(self, patch: "Patch", file_name: str, file_content: IO) -> (str, IO):
        checked_sections: list[Path] = []

        for section in self.sections if self.sections is not None else []:
            section_path = patch.path / section
            if not section_path.is_relative_to(patch.path):
                raise PathOutsidePatch(section_path, patch.path)

            checked_sections += section_path
        # for every file in the sections, check if they are inside the patch.

        patch_content = BytesIO(
            wstrt.patch_data(
                file_content.read(),
                region=self.region,
                https=self.https,
                domain=self.domain,
                sections=checked_sections
            )
        )

        return file_name, patch_content

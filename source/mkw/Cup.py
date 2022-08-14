from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from source.mkw import ModConfig


class Cup:
    """
    class that represent a mario kart wii track cup
    """

    __slots__ = ["_tracks", "cup_name", "cup_id"]
    _last_cup_id = 0

    def __init__(self, tracks: list["Track | TrackGroup"], cup_name: str | None = None):
        self._tracks = tracks[:4]

        self.cup_id = self.__class__._last_cup_id
        self.cup_name = cup_name if cup_name is not None else self.cup_id
        self.__class__._last_cup_id += 1

    def __repr__(self):
        return f"<Cup name={self.cup_name} id={self.cup_id} tracks={self._tracks}>"

    def get_default_cticon(self, mod_config: "ModConfig") -> Image.Image:
        """
        Get the default cticon for this cup
        :return: the default cticon
        """
        from source.mkw.ModConfig import CT_ICON_SIZE

        ct_icon = Image.new("RGBA", (CT_ICON_SIZE, CT_ICON_SIZE))
        default_font_path = str(mod_config.get_default_font().resolve())
        draw = ImageDraw.Draw(ct_icon)

        draw.text(
            (4, 4),
            "CT",
            (255, 165, 0),
            font=ImageFont.truetype(default_font_path, 90),
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )
        draw.text(
            (5, 80),
            f"{self.cup_id:03}",
            (255, 165, 0),
            font=ImageFont.truetype(default_font_path, 60),
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

        return ct_icon

    def get_cticon(self, mod_config: "ModConfig") -> Image.Image:
        """
        Get the cticon for this cup
        :return: the cticon
        """
        path = mod_config.get_mod_directory() / f"_CUPS/{self.cup_name}.png"
        if path.exists(): return Image.open(path)
        # if the icon doesn't exist, use the default automatically generated one
        return self.get_default_cticon(mod_config=mod_config)

    def get_ctfile(self, mod_config: "ModConfig", template: str) -> str:
        """
        Get the ctfile for this cup
        :return: the ctfile
        """
        ctfile = f'C "{self.cup_name}"\n'
        for track in self._tracks: ctfile += track.get_ctfile(mod_config, template)
        ctfile += "\n"

        return ctfile


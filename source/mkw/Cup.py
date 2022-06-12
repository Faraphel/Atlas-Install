# class that represent a mario kart wii cup
from PIL import Image


class Cup:
    __slots__ = ["_tracks", "cup_id"]
    _last_cup_id = 0

    def __init__(self, tracks: list["Track | TrackGroup"], cup_id: str | None = None):
        self._tracks = tracks[:4]

        if cup_id is None:
            cup_id = self.__class__._last_cup_id
            self.__class__._last_cup_id += 1

        self.cup_id = cup_id

    def __repr__(self):
        return f"<Cup id={self.cup_id} tracks={self._tracks}>"

    def get_cup_icon(self) -> Image.Image:
        ...

    def get_ctfile(self, mod_config: "ModConfig") -> str:
        """
        Get the ctfile for this cup
        :return: the ctfile
        """
        ctfile = f'C "{self.cup_id}"\n'
        for track in self._tracks: ctfile += track.get_ctfile(mod_config=mod_config)
        ctfile += "\n"

        return ctfile

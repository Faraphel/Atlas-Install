from PIL import Image, ImageDraw, ImageFont
import os

from source.Track import Track, TrackGroup, get_trackdata_from_json


class Cup:
    icon_dir = None
    default_track = None

    def __init__(self,
                 name: str = None,
                 id: int = 0,
                 track1: [Track, TrackGroup] = None,
                 track2: [Track, TrackGroup] = None,
                 track3: [Track, TrackGroup] = None,
                 track4: [Track, TrackGroup] = None,
                 *args, **kwargs):
        """
        class of a cup
        :param name: name of the cup
        :param track1: first track
        :param track2: second track
        :param track3: third track
        :param track4: fourth track
        :param args: other args that I could add in the future
        :param kwargs: other kwargs that I could add in the future
        """

        self.name = name
        self.id = id
        self.tracks = [
            track1 if track1 else self.default_track.copy() if self.default_track else None,
            track2 if track2 else self.default_track.copy() if self.default_track else None,
            track3 if track3 else self.default_track.copy() if self.default_track else None,
            track4 if track4 else self.default_track.copy() if self.default_track else None,
        ]

    def get_ctfile(self, *args, **kwargs) -> str:
        """
        get the ctfile definition for the cup
        :param race: is it a text used for Race_*.szs ?
        :return: ctfile definition for the cup
        """
        ctfile_cup = f'\nC "{self.name}"\n'
        for track in self.tracks:
            ctfile_cup += track.get_ctfile(*args, **kwargs)
        return ctfile_cup

    def load_from_json(self, cup: dict, *args, **kwargs):
        """
        load the cup from a dictionnary
        :param cup: dictionnary cup
        """
        for key, value in cup.items():  # load all value in the json as class attribute
            if key == "tracks":  # if the key is tracks
                for i, track_json in enumerate(value):  # load all tracks from their json
                    self.tracks[i] = get_trackdata_from_json(track_json)

            else:
                setattr(self, key, value)

        return self

    def get_tracks(self):
        for trackdata in self.tracks:
            for track in trackdata.get_tracks():
                yield track

    def get_icon(self, font_path: str = "./assets/SuperMario256.ttf") -> Image:
        """
        :param font_path: path to the font used to generate icon
        :return: cup icon
        """
        cup_icon = None

        for name in [self.id, self.name]:
            if os.path.exists(f"{self.icon_dir}/{name}.png"):
                cup_icon = Image.open(f"{self.icon_dir}/{name}.png").resize((128, 128))

        if not cup_icon:
            cup_icon = Image.new("RGBA", (128, 128))
            draw = ImageDraw.Draw(cup_icon)
            font = ImageFont.truetype(font_path, 90)
            draw.text((4, 4), "CT", (255, 165, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
            font = ImageFont.truetype(font_path, 60)
            draw.text((5, 80), "%03i" % self.id, (255, 165, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))

        return cup_icon

from dataclasses import dataclass

from source.mkw import Slot
from source.translation import translate as _


class OriginalTrackNotFound(Exception):
    def __init__(self, track_data: any):
        super().__init__(_("CANNOT_FIND_ORIGINAL_TRACK", ' "', track_data, '" '))


@dataclass(init=True, slots=True)
class OriginalTrack:
    """
    An object representing one of the original track / arena of the game
    """

    name: str 
    slot: Slot

    def __post_init__(self):
        if isinstance(self.slot, str): self.slot = Slot.get(normal=self.slot)


all_original_tracks: list[OriginalTrack] = [
    OriginalTrack(name="beginner_course", slot=Slot.get(normal="T11")),
    OriginalTrack(name="farm_course", slot="T12"),
    OriginalTrack(name="kinoko_course", slot="T13"),
    OriginalTrack(name="factory_course", slot="T14"),

    OriginalTrack(name="castle_course", slot="T21"),
    OriginalTrack(name="shopping_course", slot="T22"),
    OriginalTrack(name="boardcross_course", slot="T23"),
    OriginalTrack(name="truck_course", slot="T24"),

    OriginalTrack(name="senior_course", slot="T31"),
    OriginalTrack(name="water_course", slot="T32"),
    OriginalTrack(name="treehouse_course", slot="T33"),
    OriginalTrack(name="volcano_course", slot="T34"),

    OriginalTrack(name="desert_course", slot="T41"),
    OriginalTrack(name="ridgehighway_course", slot="T42"),
    OriginalTrack(name="koopa_course", slot="T43"),
    OriginalTrack(name="rainbow_course", slot="T44"),

    # retro tracks
    OriginalTrack(name="old_peach_gc", slot="T51"),
    OriginalTrack(name="old_falls_ds", slot="T52"),
    OriginalTrack(name="old_obake_sfc", slot="T53"),
    OriginalTrack(name="old_mario_64", slot="T54"),

    OriginalTrack(name="old_sherbet_64", slot="T61"),
    OriginalTrack(name="old_heyho_gba", slot="T62"),
    OriginalTrack(name="old_town_ds", slot="T63"),
    OriginalTrack(name="old_waluigi_gc", slot="T64"),

    OriginalTrack(name="old_desert_ds", slot="T71"),
    OriginalTrack(name="old_koopa_gba", slot="T72"),
    OriginalTrack(name="old_donkey_64", slot="T73"),
    OriginalTrack(name="old_mario_gc", slot="T74"),

    OriginalTrack(name="old_mario_sfc", slot="T81"),
    OriginalTrack(name="old_garden_ds", slot="T82"),
    OriginalTrack(name="old_donkey_gc", slot="T83"),
    OriginalTrack(name="old_koopa_64", slot="T84"),

    # wii arena
    OriginalTrack(name="block_battle", slot="A11"),
    OriginalTrack(name="venice_battle", slot="A12"),
    OriginalTrack(name="skate_battle", slot="A13"),
    OriginalTrack(name="casino_battle", slot="A14"),
    OriginalTrack(name="sand_battle", slot="A15"),

    # retro arena
    OriginalTrack(name="old_battle4_sfc", slot="A21"),
    OriginalTrack(name="old_battle3_gba", slot="A22"),
    OriginalTrack(name="old_matenro_64", slot="A23"),
    OriginalTrack(name="old_CookieLand_gc", slot="A24"),
    OriginalTrack(name="old_House_ds", slot="A25"),
]


def get(**track_datas) -> OriginalTrack:
    """
    Get a original track object from keys and its value
    :param track_datas: dictionary of track key and their value
    :return: the corresponding original track
    """
    try:
        return next(filter(
            lambda og_track: all(getattr(og_track, key) == value for key, value in track_datas.items()),
            all_original_tracks
        ))
    except StopIteration: raise OriginalTrackNotFound(track_datas)


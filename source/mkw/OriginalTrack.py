from dataclasses import dataclass

from source.mkw import Slot
from source.translation import translate as _


class OriginalTrackNotFound(Exception):
    def __init__(self, track_data: any):
        super().__init__(_("CANNOT_FIND_ORIGINAL_TRACK", ' "', track_data, '" '))


@dataclass(init=True, slots=True, frozen=True)
class OriginalTrack:
    """
    An object representing one of the original track / arena of the game
    """

    name: str 
    slot: Slot
    nickname: str


all_original_tracks: list[OriginalTrack] = [
    OriginalTrack(name="beginner_course", slot="T11", nickname="LC"),
    OriginalTrack(name="farm_course", slot="T12", nickname="MMM"),
    OriginalTrack(name="kinoko_course", slot="T13", nickname="MG"),
    OriginalTrack(name="factory_course", slot="T14", nickname="TF"),

    OriginalTrack(name="castle_course", slot="T21", nickname="MC"),
    OriginalTrack(name="shopping_course", slot="T22", nickname="CM"),
    OriginalTrack(name="boardcross_course", slot="T23", nickname="DKS"),
    OriginalTrack(name="truck_course", slot="T24", nickname="WGM"),

    OriginalTrack(name="senior_course", slot="T31", nickname="DC"),
    OriginalTrack(name="water_course", slot="T32", nickname="KC"),
    OriginalTrack(name="treehouse_course", slot="T33", nickname="MT"),
    OriginalTrack(name="volcano_course", slot="T34", nickname="GV"),

    OriginalTrack(name="desert_course", slot="T41", nickname="DDR"),
    OriginalTrack(name="ridgehighway_course", slot="T42", nickname="MH"),
    OriginalTrack(name="koopa_course", slot="T43", nickname="BC"),
    OriginalTrack(name="rainbow_course", slot="T44", nickname="RR"),

    # retro tracks
    OriginalTrack(name="old_peach_gc", slot="T51", nickname="gPB"),
    OriginalTrack(name="old_falls_ds", slot="T52", nickname="dYF"),
    OriginalTrack(name="old_obake_sfc", slot="T53", nickname="sGV2"),
    OriginalTrack(name="old_mario_64", slot="T54", nickname="nMR"),

    OriginalTrack(name="old_sherbet_64", slot="T61", nickname="nSL"),
    OriginalTrack(name="old_heyho_gba", slot="T62", nickname="gSGB"),
    OriginalTrack(name="old_town_ds", slot="T63", nickname="dDS"),
    OriginalTrack(name="old_waluigi_gc", slot="T64", nickname="gWS"),

    OriginalTrack(name="old_desert_ds", slot="T71", nickname="dDH"),
    OriginalTrack(name="old_koopa_gba", slot="T72", nickname="gBC3"),
    OriginalTrack(name="old_donkey_64", slot="T73", nickname="nDKJP"),
    OriginalTrack(name="old_mario_gc", slot="T74", nickname="gMC"),

    OriginalTrack(name="old_mario_sfc", slot="T81", nickname="sMC3"),
    OriginalTrack(name="old_garden_ds", slot="T82", nickname="dPG"),
    OriginalTrack(name="old_donkey_gc", slot="T83", nickname="gDKM"),
    OriginalTrack(name="old_koopa_64", slot="T84", nickname="nBC"),

    # wii arena
    OriginalTrack(name="block_battle", slot="A11", nickname="aBP"),
    OriginalTrack(name="venice_battle", slot="A12", nickname="aDP"),
    OriginalTrack(name="skate_battle", slot="A13", nickname="aFS"),
    OriginalTrack(name="casino_battle", slot="A14", nickname="aCCW"),
    OriginalTrack(name="sand_battle", slot="A15", nickname="aTD"),

    # retro arena
    OriginalTrack(name="old_battle4_sfc", slot="A21", nickname="asBC4"),
    OriginalTrack(name="old_battle3_gba", slot="A22", nickname="agBC3"),
    OriginalTrack(name="old_matenro_64", slot="A23", nickname="anSS"),
    OriginalTrack(name="old_CookieLand_gc", slot="A24", nickname="agCL"),
    OriginalTrack(name="old_House_ds", slot="A25", nickname="adTH"),
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


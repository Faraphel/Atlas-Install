from dataclasses import dataclass
from source.translation import translate as _


class SlotNotFound(Exception):
    def __init__(self, slot_data: any):
        super().__init__(_("ERROR_CANNOT_FIND_SLOT") % slot_data)


@dataclass(init=True, slots=True, frozen=True, repr=True)
class Slot:
    """
    represent a game slot (arena, ...)
    """

    normal: str  # T11, T12, ...
    abbreviation: str  # LC, MMM, ...
    track_name: str  # beginner_course, farm_course, ...

    def __str__(self) -> str: return self.normal
    def __eq__(self, other) -> bool: return any(getattr(self, key) == other for key in self.__slots__)


all_slots: list[Slot] = [
    Slot(normal="T11", abbreviation="LC", track_name="beginner_course"),
    Slot(normal="T12", abbreviation="MMM", track_name="farm_course"),
    Slot(normal="T13", abbreviation="MG", track_name="kinoko_course"),
    Slot(normal="T14", abbreviation="TF", track_name="factory_course"),

    Slot(normal="T21", abbreviation="MC", track_name="castle_course"),
    Slot(normal="T22", abbreviation="CM", track_name="shopping_course"),
    Slot(normal="T23", abbreviation="DKS", track_name="boardcross_course"),
    Slot(normal="T24", abbreviation="WGM", track_name="truck_course"),

    Slot(normal="T31", abbreviation="DC", track_name="senior_course"),
    Slot(normal="T32", abbreviation="KC", track_name="water_course"),
    Slot(normal="T33", abbreviation="MT", track_name="treehouse_course"),
    Slot(normal="T34", abbreviation="GV", track_name="volcano_course"),

    Slot(normal="T41", abbreviation="DDR", track_name="desert_course"),
    Slot(normal="T42", abbreviation="MH", track_name="ridgehighway_course"),
    Slot(normal="T43", abbreviation="BC", track_name="koopa_course"),
    Slot(normal="T44", abbreviation="RR", track_name="rainbow_course"),

    # retro tracks
    Slot(normal="T51", abbreviation="gPB", track_name="old_peach_gc"),
    Slot(normal="T52", abbreviation="dYF", track_name="old_falls_ds"),
    Slot(normal="T53", abbreviation="sGV2", track_name="old_obake_sfc"),
    Slot(normal="T54", abbreviation="nMR", track_name="old_mario_64"),

    Slot(normal="T61", abbreviation="nSL", track_name="old_sherbet_64"),
    Slot(normal="T62", abbreviation="gSGB", track_name="old_heyho_gba"),
    Slot(normal="T63", abbreviation="dDS", track_name="old_town_ds"),
    Slot(normal="T64", abbreviation="gWS", track_name="old_waluigi_gc"),

    Slot(normal="T71", abbreviation="dDH", track_name="old_desert_ds"),
    Slot(normal="T72", abbreviation="gBC3", track_name="old_koopa_gba"),
    Slot(normal="T73", abbreviation="nDKJP", track_name="old_donkey_64"),
    Slot(normal="T74", abbreviation="gMC", track_name="old_mario_gc"),

    Slot(normal="T81", abbreviation="sMC3", track_name="old_mario_sfc"),
    Slot(normal="T82", abbreviation="dPG", track_name="old_garden_ds"),
    Slot(normal="T83", abbreviation="gDKM", track_name="old_donkey_gc"),
    Slot(normal="T84", abbreviation="nBC", track_name="old_koopa_64"),

    # wii arena
    Slot(normal="A11", abbreviation="aBP", track_name="block_battle"),
    Slot(normal="A12", abbreviation="aDP", track_name="venice_battle"),
    Slot(normal="A13", abbreviation="aFS", track_name="skate_battle"),
    Slot(normal="A14", abbreviation="aCCW", track_name="casino_battle"),
    Slot(normal="A15", abbreviation="aTD", track_name="sand_battle"),

    # retro arena
    Slot(normal="A21", abbreviation="asBC4", track_name="old_battle4_sfc"),
    Slot(normal="A22", abbreviation="agBC3", track_name="old_battle3_gba"),
    Slot(normal="A23", abbreviation="anSS", track_name="old_matenro_64"),
    Slot(normal="A24", abbreviation="agCL", track_name="old_CookieLand_gc"),
    Slot(normal="A25", abbreviation="adTH", track_name="old_House_ds"),
]


def get(**slot_datas) -> Slot:
    """
    Get a original slot object from keys and its value
    :param slot_datas: dictionary of track key and their value
    :return: the corresponding slot
    """
    try:
        return next(filter(
            lambda slot: all(getattr(slot, key) == value for key, value in slot_datas.items()),
            all_slots
        ))
    except StopIteration: raise SlotNotFound(slot_datas)


def find(value) -> Slot:
    """
    Return a slot from any value of any key.
    :param value: the value used to search the slot
    :return: the corresponding slot
    """
    try: return next(filter(lambda slot: slot == value, all_slots))
    except StopIteration: raise SlotNotFound(value)

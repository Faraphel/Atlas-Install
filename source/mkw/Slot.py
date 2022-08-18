from dataclasses import dataclass


class SlotNotFound(Exception):
    def __init__(self, slot_data: any):
        super().__init__(_("CANNOT_FIND_SLOT", ' "', slot_data, '" '))


@dataclass(init=True, slots=True, frozen=True, repr=True)
class Slot:
    """
    represent a game slot (arena, ...)
    """

    normal: str  # T11, T12, ...
    abbreviation: str  # LC, MMM, ...

    def __str__(self) -> str: return self.normal
    def __eq__(self, other) -> bool: return any(getattr(self, key) == other for key in self.__slots__)


all_slots: list[Slot] = [
    Slot(normal="T11", abbreviation="LC"),
    Slot(normal="T12", abbreviation="MMM"),
    Slot(normal="T13", abbreviation="MG"),
    Slot(normal="T14", abbreviation="TF"),

    Slot(normal="T21", abbreviation="MC"),
    Slot(normal="T22", abbreviation="CM"),
    Slot(normal="T23", abbreviation="DKS"),
    Slot(normal="T24", abbreviation="WGM"),

    Slot(normal="T31", abbreviation="DC"),
    Slot(normal="T32", abbreviation="KC"),
    Slot(normal="T33", abbreviation="MT"),
    Slot(normal="T34", abbreviation="GV"),

    Slot(normal="T41", abbreviation="DDR"),
    Slot(normal="T42", abbreviation="MH"),
    Slot(normal="T43", abbreviation="BC"),
    Slot(normal="T44", abbreviation="RR"),

    # retro tracks
    Slot(normal="T51", abbreviation="gPB"),
    Slot(normal="T52", abbreviation="dYF"),
    Slot(normal="T53", abbreviation="sGV2"),
    Slot(normal="T54", abbreviation="nMR"),

    Slot(normal="T61", abbreviation="nSL"),
    Slot(normal="T62", abbreviation="gSGB"),
    Slot(normal="T63", abbreviation="dDS"),
    Slot(normal="T64", abbreviation="gWS"),

    Slot(normal="T71", abbreviation="dDH"),
    Slot(normal="T72", abbreviation="gBC3"),
    Slot(normal="T73", abbreviation="nDKJP"),
    Slot(normal="T74", abbreviation="gMC"),

    Slot(normal="T81", abbreviation="sMC3"),
    Slot(normal="T82", abbreviation="dPG"),
    Slot(normal="T83", abbreviation="gDKM"),
    Slot(normal="T84", abbreviation="nBC"),

    # wii arena
    Slot(normal="A11", abbreviation="aBP"),
    Slot(normal="A12", abbreviation="aDP"),
    Slot(normal="A13", abbreviation="aFS"),
    Slot(normal="A14", abbreviation="aCCW"),
    Slot(normal="A15", abbreviation="aTD"),

    # retro arena
    Slot(normal="A21", abbreviation="asBC4"),
    Slot(normal="A22", abbreviation="agBC3"),
    Slot(normal="A23", abbreviation="anSS"),
    Slot(normal="A24", abbreviation="agCL"),
    Slot(normal="A25", abbreviation="adTH"),
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

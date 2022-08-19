from dataclasses import dataclass

from source.translation import translate as _


class ColorNotFound(Exception):
    def __init__(self, color_data: any):
        super().__init__(_("CANNOT_FIND_COLOR", ' "', color_data, '"'))


@dataclass(init=True, slots=True)
class MKWColor:
    """
    Represent a color that can be used inside MKW files
    """
    
    bmg: str 
    hexadecimal: hex 
    name: str
    
    @property
    def color_code(self) -> str:
        """
        Return a color code that can be used in tkinter
        :return: the color code
        """
        return f"#{self.hexadecimal:06X}"

    @property
    def raw(self) -> str:
        """
        return the special control character to start coloring a text
        :return: return the color control character
        """
        return r"\c{" + self.bmg + "}"

    def color_text(self, text: str) -> str:
        """
        color a text, then reset the color
        :param text: text to color
        :return: return the formatted text with the color
        """
        return f'{self.raw}{text}{get(bmg="off").raw}'


all_colors: list[MKWColor] = [
    MKWColor(bmg="white",  hexadecimal=0xFFFFFF, name="white"),
    MKWColor(bmg="clear",  hexadecimal=0x000000, name="clear"),
    MKWColor(bmg="off",    hexadecimal=0xDDDDDD, name="off"),

    MKWColor(bmg="yor7",   hexadecimal=0xF5090B, name="apple red"),
    MKWColor(bmg="yor6",   hexadecimal=0xE82C09, name="dark red"),
    MKWColor(bmg="yor5",   hexadecimal=0xE65118, name="dark orange"),  # flame
    MKWColor(bmg="yor4",   hexadecimal=0xFF760E, name="orange"),  # pumpkin
    MKWColor(bmg="yor3",   hexadecimal=0xFFA61F, name="light orange"),  # bright yellow
    MKWColor(bmg="yor2",   hexadecimal=0xFEBC1F, name="yellow"),  # ripe mango
    MKWColor(bmg="yor1",   hexadecimal=0xFFE71F, name="light yellow"),
    MKWColor(bmg="yor0",   hexadecimal=0xFFFF22, name="neon yellow"),
    MKWColor(bmg="blue2",  hexadecimal=0x1170EC, name="dark blue"),
    MKWColor(bmg="blue1",  hexadecimal=0x75B5F6, name="azure"),
    MKWColor(bmg="green",  hexadecimal=0x0EB00A, name="green"),
    MKWColor(bmg="yellow", hexadecimal=0xFFFD1E, name="neon yellow 2"),
    MKWColor(bmg="red4",   hexadecimal=0xEE0C10, name="vivid red"),
    MKWColor(bmg="red3",   hexadecimal=0xFF0308, name="red"),
    MKWColor(bmg="red2",   hexadecimal=0xF14A4E, name="light red"),
    MKWColor(bmg="red1",   hexadecimal=0xE46C74, name="pink"),
]


def get(**color_datas) -> MKWColor:
    """
    Get a original track object from keys and its value
    :param color_datas: dictionary of track key and their value
    :return: the corresponding original track
    """
    try:
        return next(filter(
            lambda color: all(getattr(color, key) == value for key, value in color_datas.items()),
            all_colors
        ))
    except StopIteration: raise ColorNotFound(color_datas)

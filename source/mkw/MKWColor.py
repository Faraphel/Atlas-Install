
class ColorNotFound(Exception):
    def __init__(self, color_data: any):
        super().__init__(f'Can\'t find color "{color_data}"')


class MKWColor:
    """
    Represent a color that can be used inside MKW files
    """

    all_colors: list[dict] = [
        {"bmg": "yor7",   "hex": 0xF5090B, "name": "apple red"},
        {"bmg": "yor6",   "hex": 0xE82C09, "name": "dark red"},
        {"bmg": "yor5",   "hex": 0xE65118, "name": "dark orange"},  # flame
        {"bmg": "yor4",   "hex": 0xFF760E, "name": "orange"},  # pumpkin
        {"bmg": "yor3",   "hex": 0xFFA61F, "name": "light orange"},  # bright yellow
        {"bmg": "yor2",   "hex": 0xFEBC1F, "name": "yellow"},  # ripe mango
        {"bmg": "yor1",   "hex": 0xFFE71F, "name": "light yellow"},
        {"bmg": "yor0",   "hex": 0xFFFF22, "name": "neon yellow"},
        {"bmg": "blue2",  "hex": 0x1170EC, "name": "dark blue"},
        {"bmg": "blue1",  "hex": 0x75B5F6, "name": "azure"},
        {"bmg": "green",  "hex": 0x0EB00A, "name": "green"},
        {"bmg": "yellow", "hex": 0xFFFD1E, "name": "neon yellow 2"},
        {"bmg": "red4",   "hex": 0xEE0C10, "name": "vivid red"},
        {"bmg": "red3",   "hex": 0xFF0308, "name": "red"},
        {"bmg": "red2",   "hex": 0xF14A4E, "name": "light red"},
        {"bmg": "red1",   "hex": 0xE46C74, "name": "pink"},
        {"bmg": "white",  "hex": 0xFFFFFF, "name": "white"},
        {"bmg": "clear",  "hex": 0x000000, "name": "clear"},
        {"bmg": "off",    "hex": 0x998C86, "name": "off"},
    ]

    __slots__ = ("bmg", "hex", "name")

    def __init__(self, color_data: any, color_key: str = "name"):
        colors = list(filter(lambda color: color[color_key] == color_data, self.all_colors))
        if len(colors) == 0: raise ColorNotFound(color_data)

        for key, value in colors[0].items():
            setattr(self, key, value)


def bmg_color_text(color_name: str, text: str) -> str:
    """
    Useful shortcut to color a text
    :param color_name: name of the color
    :param text: text to color
    :return: return the formatted text with the color
    """
    return r"\c{" + MKWColor(color_name).bmg + "}" + text + r"\c{" + MKWColor('off').bmg + "}"

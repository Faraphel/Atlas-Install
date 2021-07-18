from PIL import Image, ImageFont, ImageDraw
import math
import os


def get_cup_icon(cup_id, font_path: str = "./file/SuperMario256.ttf", cup_icon_dir: str = "./file/cup_icon"):
    """
    :param cup_icon_dir: directory to cup icon
    :param font_path: path to the font used to generate icon
    :param cup_id: id of the cup
    :return: cup icon
    """
    if os.path.exists(f"{cup_icon_dir}/{cup_id}.png"):
        cup_icon = Image.open(f"{cup_icon_dir}/{cup_id}.png").resize((128, 128))

    else:
        cup_icon = Image.new("RGBA", (128, 128))
        draw = ImageDraw.Draw(cup_icon)
        font = ImageFont.truetype(font_path, 90)
        draw.text((4 - 2, 4 - 2), "CT", (0, 0, 0), font=font)
        draw.text((4 + 2, 4 - 2), "CT", (0, 0, 0), font=font)
        draw.text((4 - 2, 4 + 2), "CT", (0, 0, 0), font=font)
        draw.text((4 + 2, 4 + 2), "CT", (0, 0, 0), font=font)
        draw.text((4, 4), "CT", (255, 165, 0), font=font)

        font = ImageFont.truetype(font_path, 60)
        draw.text((5 - 2, 80 - 2), "%03i" % cup_id, (0, 0, 0), font=font)
        draw.text((5 + 2, 80 - 2), "%03i" % cup_id, (0, 0, 0), font=font)
        draw.text((5 - 2, 80 + 2), "%03i" % cup_id, (0, 0, 0), font=font)
        draw.text((5 + 2, 80 + 2), "%03i" % cup_id, (0, 0, 0), font=font)

        draw.text((5, 80), "%03i" % cup_id, (255, 165, 0), font=font)
    return cup_icon


def get_cticon(self):
    """
    get all cup icon into a single image
    :return: ct_icon image
    """
    CT_ICON_WIDTH = 128
    icon_files = ["left", "right"]

    total_cup_count = math.ceil(len(self.all_tracks) / 4)
    ct_icon = Image.new("RGBA",
                        (CT_ICON_WIDTH, CT_ICON_WIDTH * (total_cup_count + 2)))  # +2 because of left and right arrow

    icon_files.extend([str(i) for i, cup in enumerate(self.ordered_cups)])  # adding ordered cup id
    icon_files.extend(["_"] * ((len(self.unordered_tracks) // 4) + 1))  # creating unordered track icon

    for i, id in enumerate(icon_files):
        cup_icon = get_cup_icon(i)
        ct_icon.paste(cup_icon, (0, i * CT_ICON_WIDTH))

    return ct_icon

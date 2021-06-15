from PIL import Image, ImageFont, ImageDraw
import json
import math
import os


def patch_ct_icon(self):
    try:
        with open("./ct_config.json", encoding="utf8") as f: config = json.load(f)

        cup_number = len(config["cup"]) + math.ceil(len(config["tracks_list"]) / 4)
        ct_icon = Image.new("RGBA", (128, 128 * (cup_number + 2)))

        files = ["left", "right"]
        files.extend(config["cup"].keys())
        files.extend(["_"] * ((len(config["tracks_list"]) // 4) + 1))

        for i, id in enumerate(files):
            if os.path.exists(f"./file/cup_icon/{id}.png"):
                cup_icon = Image.open(f"./file/cup_icon/{id}.png").resize((128, 128))

            else:
                cup_icon = Image.new("RGBA", (128, 128))
                draw = ImageDraw.Draw(cup_icon)
                font = ImageFont.truetype("./file/SuperMario256.ttf", 90)
                draw.text((4 - 2, 4 - 2), "CT", (0, 0, 0), font=font)
                draw.text((4 + 2, 4 - 2), "CT", (0, 0, 0), font=font)
                draw.text((4 - 2, 4 + 2), "CT", (0, 0, 0), font=font)
                draw.text((4 + 2, 4 + 2), "CT", (0, 0, 0), font=font)
                draw.text((4, 4), "CT", (255, 165, 0), font=font)

                font = ImageFont.truetype("./file/SuperMario256.ttf", 60)
                draw.text((5 - 2, 80 - 2), "%03i" % (i-10), (0, 0, 0), font=font)  # i-10 car on ne compte pas les 8 coupes
                draw.text((5 + 2, 80 - 2), "%03i" % (i-10), (0, 0, 0), font=font)  # de base (0-7), la coupe aléatoire, et
                draw.text((5 - 2, 80 + 2), "%03i" % (i-10), (0, 0, 0), font=font)  # les icones droite et gauche.
                draw.text((5 + 2, 80 + 2), "%03i" % (i-10), (0, 0, 0), font=font)

                draw.text((5, 80), "%03i" % (i-10), (255, 165, 0), font=font)

            ct_icon.paste(cup_icon, (0, i * 128))

        ct_icon.save("./file/ct_icons.tpl.png")

    except:
        self.log_error()

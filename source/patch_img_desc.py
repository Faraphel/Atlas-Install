from PIL import Image
import glob

from .definition import *


def patch_img_desc(self):
    try:
        il = Image.open("./file/img_desc/illustration.png")
        il_16_9 = il.resize((832, 456))
        il_4_3 = il.resize((608, 456))

        for file_lang in glob.glob("./file/img_desc/??.png"):
            img_lang = Image.open(file_lang)
            img_lang_16_9 = img_lang.resize((832, 456))
            img_lang_4_3 = img_lang.resize((608, 456))

            new_16_9 = Image.new("RGBA", (832, 456), (0, 0, 0, 255))
            new_16_9.paste(il_16_9, (0, 0), il_16_9)
            new_16_9.paste(img_lang_16_9, (0, 0), img_lang_16_9)
            new_16_9.save(f"./file/strapA_16_9_832x456{get_filename(get_nodir(file_lang))}.png")

            new_4_3 = Image.new("RGBA", (608, 456), (0, 0, 0, 255))
            new_4_3.paste(il_4_3, (0, 0), il_4_3)
            new_4_3.paste(img_lang_4_3, (0, 0), img_lang_4_3)
            new_4_3.save(f"./file/strapA_608x456{get_filename(get_nodir(file_lang))}.png")

    except:
        self.log_error()

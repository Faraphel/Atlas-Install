from source.definition import *
import os

from .exception import *


class Game:
    def __init__(self, path: str, region_ID: str = "P", game_ID: str = "RMCP01"):
        if not os.path.exists(path): raise InvalidGamePath()
        self.extension = get_extension(path).upper()
        self.path = path
        self.region = region_id_to_name[region_ID]
        self.region_ID = region_ID
        self.game_ID = game_ID

    from .convert_to import convert_to
    from .extract import extract
    from .install_mod import install_mod
    from .patch_autoadd import patch_autoadd
    from .patch_bmg import patch_bmg
    from .patch_file import patch_file
    from .patch_image import patch_image
    from .patch_img_desc import patch_img_desc
    from .patch_track import patch_track

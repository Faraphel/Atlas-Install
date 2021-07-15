from .definition import region_ID


class Game:
    def __init__(self, path: str, region: str = "PAL"):
        self.path = path
        self.region_ID = region_ID[region]
        self.region = region

    def extract_game(self):
        pass

    def install_mod(self):
        pass

    def convert_to(self, format: str = "FST"):
        """
        :param format: game format (ISO, WBFS, ...)
        :return: converted game path
        """
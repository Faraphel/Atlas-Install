from source.CT_Config import CT_Config
from source.Option import Option
from source.Game import Game
from source.Gui.Main import Main
from source.Gui.TrackConfiguration import TrackConfiguration
from source.Translation import Translator


class Common:
    def __init__(self):
        """
        Common allow to store multiple object that need each other and still make the code readable enough without
        having to access an object with some obscure way
        """

        self.json_frame_filter = None
        self.translator = Translator(common=self)
        self.translate = self.translator.translate  # shortcut for the method

        self.option = Option().load_from_file("./option.json")
        self.ct_config = CT_Config()
        self.game = Game(common=self)

        self.gui_main = Main(common=self)

    def show_gui_track_configuration(self): TrackConfiguration(common=self)
    def mainloop(self): self.gui_main.mainloop()

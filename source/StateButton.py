from tkinter import *

def StateButton(self, enable=True):
    button = [
        self.button_game_extract,
        self.button_install_mod,
        self.button_prepare_file
    ]
    for widget in button:
        if enable:
            widget.config(state=NORMAL)
        else:
            widget.config(state=DISABLED)

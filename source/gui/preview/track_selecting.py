import tkinter
from tkinter import ttk
import re

from source.mkw.MKWColor import MKWColor
from source.gui.preview import AbstractPreviewWindow
from source.gui import better_gui_error


ModConfig: any


class Window(AbstractPreviewWindow):

    name = "track_selecting"

    def __init__(self, mod_config: "ModConfig", template_variable: tkinter.StringVar = None):
        super().__init__(mod_config, template_variable)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grab_set()

        if template_variable is None: template_variable = tkinter.StringVar()
        self.mod_config = mod_config

        self.entry_template_input = ttk.Entry(self, width=100, textvariable=template_variable)
        self.entry_template_input.grid(row=1, column=1, columnspan=2, sticky="NEWS")
        self.entry_template_input.bind("<Return>", self.preview)

        self.text_track_format = tkinter.Text(self, width=40, bg="black", fg=MKWColor("off").color_code, state=tkinter.DISABLED)
        self.text_track_format.grid(row=2, column=1, sticky="NEWS")
        
        self.text_track_select = tkinter.Text(self, width=20, bg="black", state=tkinter.DISABLED)
        self.text_track_select.grid(row=2, column=2, sticky="NEWS")
        
        # if a textbox is scrolled, the scrollbar and the other textbox will be affected too
        def scroll_textbox(first: int, last: int):
            self.scrollbar_track_preview.set(first, last)
            self.text_track_format.yview("moveto", first)
            self.text_track_select.yview("moveto", first)

        # if the scrollbar is scrolled, then the two textbox are affected
        self.scrollbar_track_preview = ttk.Scrollbar(self, 
            command=lambda *args: (
                self.text_track_format.yview(*args), 
                self.text_track_select.yview(*args)
            )
        )
        self.scrollbar_track_preview.grid(row=2, column=3, sticky="NEWS")

        self.text_track_format.configure(yscrollcommand=scroll_textbox)
        self.text_track_select.configure(yscrollcommand=scroll_textbox)

        self.text_track_select.tag_configure("True", foreground="white", background="green")
        self.text_track_select.tag_configure("False", foreground="white", background="red")

        self.refresh_tracks_format()

    def refresh_tracks_format(self) -> None:
        """
        Preview all the tracks name with the track format
        :return:
        """
        self.text_track_format.configure(state=tkinter.NORMAL)
        self.text_track_format.delete(1.0, tkinter.END)

        # insert all the tracks representation
        for track in self.mod_config.get_tracks():
            self.text_track_format.insert(tkinter.END, f"{track}\n")

        self.text_track_format.configure(state=tkinter.DISABLED)
    
    @better_gui_error
    def preview(self, event: tkinter.Event = None) -> None:
        """
        Preview all the tracks selection with the given template
        """
        self.text_track_select.configure(state=tkinter.NORMAL)
        self.text_track_select.delete(1.0, tkinter.END)

        for track in self.mod_config.get_tracks():
            value = self.mod_config.safe_eval(self.entry_template_input.get(), env={"track": track}) == "True"
            self.text_track_select.insert(tkinter.END, f"{value}\n")
            self.text_track_select.tag_add(str(value), "end-1c-1l", "end-1c")
            
        self.text_track_select.configure(state=tkinter.DISABLED)
            
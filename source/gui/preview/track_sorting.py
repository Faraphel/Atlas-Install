import tkinter
from tkinter import ttk
from typing import TYPE_CHECKING

from source.mkw import MKWColor
from source.gui.preview import AbstractPreviewWindow
from source.gui import better_gui_error

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig


class Window(AbstractPreviewWindow):
    name = "track_sorting"

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

        self.text_track_format = tkinter.Text(
            self, background="black", foreground=MKWColor.get(bmg="off").color_code, state=tkinter.DISABLED
        )
        self.text_track_format.grid(row=2, column=1, sticky="NEWS")

        self.scrollbar_track_preview = ttk.Scrollbar(self, command=self.text_track_format.yview)
        self.scrollbar_track_preview.grid(row=2, column=2, sticky="NEWS")

        self.text_track_format.configure(yscrollcommand=self.scrollbar_track_preview.set)
        self.text_track_format.tag_configure("error", background="red", foreground="white")

        self.preview()

    @better_gui_error
    def preview(self, event: tkinter.Event = None):
        """
        Preview all the tracks name with the track format
        :return:
        """
        self.text_track_format.configure(state=tkinter.NORMAL)
        self.text_track_format.delete(1.0, tkinter.END)

        template = self.entry_template_input.get()

        # insert all the tracks representation
        for track in self.mod_config.get_all_tracks(
                ignore_filter=True,
                sorting_template=template if template else None
        ):
            try:
                self.text_track_format.insert(tkinter.END, f"{track}\n")

            except Exception as exc:
                formatted_exc = str(exc).replace('\n', ' ')
                self.text_track_format.insert(tkinter.END, f"< Error: {formatted_exc} >\n")
                self.text_track_format.tag_add("error", "end-1c-1l", "end-1c")

        self.text_track_format.configure(state=tkinter.DISABLED)


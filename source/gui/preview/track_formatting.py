import tkinter
from tkinter import ttk
from source.translation import translate as _
from source.mkw.MKWColor import MKWColor


ModConfig: any


class Window(tkinter.Toplevel):
    def __init__(self, mod_config: "ModConfig"):
        super().__init__()

        self.mod_config = mod_config

        self.entry_format_input = ttk.Entry(self, width=100)
        self.entry_format_input.grid(row=1, column=1, sticky="NEWS")
        self.entry_format_input.bind("<Return>", self.preview)

        self.track_preview = tkinter.Text(self)
        self.track_preview.grid(row=2, column=1, sticky="NEWS")

    def preview(self, event: tkinter.Event = None):
        """
        Preview all the tracks name with the track format
        :return:
        """
        self.track_preview.delete(1.0, tkinter.END)

        # insert all the tracks representation
        for track in self.mod_config.get_tracks():
            try: track_repr = track.repr_format(self.mod_config, self.entry_format_input.get())
            except: track_repr = "< ERROR >"

            track_repr = track_repr.replace('\n', '\\n') + "\n"
            self.track_preview.insert(tkinter.END, track_repr)

        # add the colors
        for color in MKWColor.all_colors:
            self.track_preview.tag_configure(color["bmg"], foreground=f"#{color['hex']:06X}")
            text: str = self.track_preview.get(1.0, tkinter.END)

            tag_start: str = r"\c{" + color["bmg"] + "}"
            tag_end: str = r"\c"

            find_end = -len(tag_end)

            while find_end < len(text):
                if (find_start := text.find(tag_start, find_end + len(tag_end))) == -1: break
                if (find_end := text.find(tag_end, find_start + len(tag_start))) == -1: find_end = len(text) - 1

                text_start = text[:find_start].split("\n")
                text_start = f"{len(text_start)}.{len(text_start[-1])}"

                text_end = text[:find_end].split("\n")
                text_end = f"{len(text_end)}.{len(text_end[-1])}"

                self.track_preview.tag_add(color["bmg"], text_start, text_end)

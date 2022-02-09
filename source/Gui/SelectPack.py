from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import zipfile
import os


class SelectPack:
    def __init__(self, common):
        self.common = common

        self.root = Toplevel(self.common.gui_main.root)
        self.root.title(self.common.translate("Add a pack"))
        self.root.iconbitmap("./icon.ico")
        self.root.resizable(False, False)
        self.root.grab_set()

        self.entry_modpack_path = Entry(self.root, width=50)
        self.entry_modpack_path.grid(row=1, column=1, sticky="NEWS")

        def select_path():
            path = filedialog.askopenfilename(
                filetypes=((self.common.translate("MKW Pack"), r"*.mkwf.pack"),)
            )
            if os.path.exists(path):
                self.entry_modpack_path.delete(0, END)
                self.entry_modpack_path.insert(0, path)

        self.button_select_path = Button(
            self.root,
            text="...",
            relief=RIDGE,
            command=lambda: self.root.after(0, select_path)
        )
        self.button_select_path.grid(row=1, column=2)

        def extract_pack():
            self.progressbar_extract.grid(row=3, column=1, columnspan=2, sticky="NEWS")
            try:
                path = self.entry_modpack_path.get()
                *packname, _, _ = os.path.basename(path).split(".")
                packname = ".".join(packname)

                with zipfile.ZipFile(path) as zip_pack:
                    zip_pack.extractall(f"./Pack/{packname}/")

                self.common.gui_main.reload_ctconfig()

                messagebox.showinfo(
                    self.common.translate("Extraction"),
                    self.common.translate("The mod have been extracted !")
                )
                self.root.destroy()

            except Exception as e:
                self.progressbar_extract.grid_forget()
                raise e

        self.button_extract_modpack = Button(
            self.root,
            text=self.common.translate("Extract the modpack"),
            relief=RIDGE,
            command=extract_pack
        )
        self.button_extract_modpack.grid(row=2, column=1, columnspan=2, sticky="NEWS")

        self.progressbar_extract = ttk.Progressbar(self.root)
        self.progressbar_extract.configure(mode="indeterminate")
        self.progressbar_extract.start(50)

    def state_button(self, enable=True):
        for button in [
            self.button_extract_modpack
        ]:
            if enable: button.config(state=NORMAL)
            else: button.config(state=DISABLED)

import tkinter
from pathlib import Path
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import TYPE_CHECKING

from source.translation import translate as _

if TYPE_CHECKING:
    from source.mkw.ModConfig import ModConfig
    from source.option import Options


class Window(tkinter.Toplevel):
    """
    A window that let the user select MyStuff pack for a MKWF patch
    """

    def __init__(self, mod_config: "ModConfig", options: "Options"):
        super().__init__()

        self.root = self
        self.mod_config = mod_config
        self.options = options

        self.title(_("CONFIGURE_MYSTUFF_PATCH"))
        self.resizable(False, False)
        self.grab_set()  # the others window will be disabled, keeping only this one activated

        self.disabled_text: str = _("<", "DISABLED", ">")

        self.frame_profile = ttk.Frame(self)
        self.frame_profile.grid(row=1, column=1, sticky="NEWS")

        self.combobox_profile = ttk.Combobox(self.frame_profile, justify=tkinter.CENTER)
        self.combobox_profile.grid(row=1, column=1, sticky="NEWS")
        self.combobox_profile.bind("<<ComboboxSelected>>", self.select_profile)

        self.button_new_profile = ttk.Button(
            self.frame_profile,
            text=_("NEW_PROFILE"),
            command=self.new_profile
        )
        self.button_new_profile.grid(row=1, column=2, sticky="NEWS")

        self.button_delete_profile = ttk.Button(
            self.frame_profile,
            text=_("DELETE_PROFILE"),
            command=self.delete_profile
        )
        self.button_delete_profile.grid(row=1, column=3, sticky="NEWS")

        self.frame_mystuff_paths = ttk.Frame(self)
        self.frame_mystuff_paths.grid(row=2, column=1, sticky="NEWS")
        self.frame_mystuff_paths.grid_columnconfigure(1, weight=1)

        self.listbox_mystuff_paths = tkinter.Listbox(self.frame_mystuff_paths)
        self.listbox_mystuff_paths.grid(row=1, column=1, sticky="NEWS")
        self.scrollbar_mystuff_paths = ttk.Scrollbar(
            self.frame_mystuff_paths,
            command=self.listbox_mystuff_paths.yview
        )
        self.scrollbar_mystuff_paths.grid(row=1, column=2, sticky="NS")
        self.listbox_mystuff_paths.configure(yscrollcommand=self.scrollbar_mystuff_paths.set)

        self.frame_mystuff_paths_action = ttk.Frame(self)
        self.frame_mystuff_paths_action.grid(row=3, column=1, sticky="NEWS")

        self.button_add_mystuff_path = ttk.Button(
            self.frame_mystuff_paths_action,
            text=_("ADD_MYSTUFF"),
            command=self.add_mystuff_path
        )
        self.button_add_mystuff_path.grid(row=1, column=1)

        self.button_remove_mystuff_path = ttk.Button(
            self.frame_mystuff_paths_action,
            text=_("REMOVE_MYSTUFF"),
            command=self.remove_mystuff_path
        )
        self.button_remove_mystuff_path.grid(row=1, column=2)

        self.refresh_profiles()
        self.select_profile()

    def refresh_profiles(self) -> None:
        """
        Refresh all the profile
        """
        mystuff_packs = self.root.options.mystuff_packs.get()
        selected_mystuff_pack = self.root.options.mystuff_pack_selected.get()

        combobox_values = [self.disabled_text, *self.root.options.mystuff_packs.get()]
        self.combobox_profile.configure(values=combobox_values)
        self.combobox_profile.current(combobox_values.index(
            selected_mystuff_pack if selected_mystuff_pack in mystuff_packs else self.disabled_text
        ))

    def select_profile(self, event: tkinter.Event = None, profile_name: str = None) -> None:
        """
        Select another profile
        """
        mystuff_packs = self.root.options.mystuff_packs.get()

        profile_name = self.combobox_profile.get() if profile_name is None else profile_name
        if not profile_name in mystuff_packs: profile_name = self.disabled_text
        
        self.combobox_profile.set(profile_name)
        self.root.options.mystuff_pack_selected.set(profile_name)
        self.listbox_mystuff_paths.delete(0, tkinter.END)

        is_disabled: bool = (profile_name == self.disabled_text)
        state = tkinter.DISABLED if is_disabled else tkinter.NORMAL

        self.button_delete_profile.configure(state=state)
        for children in self.frame_mystuff_paths_action.children.values(): children.configure(state=state)

        if is_disabled: return

        profile_data = mystuff_packs[profile_name]

        for path in profile_data["paths"]:
            self.listbox_mystuff_paths.insert(tkinter.END, path)

    def new_profile(self) -> None:
        """
        Save the new profile
        """
        mystuff_packs = self.root.options.mystuff_packs.get()

        profile_name: str = self.combobox_profile.get()
        if profile_name in mystuff_packs:
            messagebox.showerror(_("ERROR"), _("MYSTUFF_PROFILE_ALREADY_EXIST"))
            return

        for banned_char in "<>":
            if banned_char in profile_name:
                messagebox.showerror(_("ERROR"), _("MYSTUFF_PROFILE_FORBIDDEN_NAME"))
                return

        mystuff_packs[profile_name] = {"paths": []}
        self.root.options.mystuff_packs.set(mystuff_packs)
        self.refresh_profiles()
        self.select_profile(profile_name=profile_name)

    def delete_profile(self) -> None:
        """
        Delete the currently selected profile
        """
        mystuff_packs = self.root.options.mystuff_packs.get()
        mystuff_packs.pop(self.root.options.mystuff_pack_selected.get())
        self.root.options.mystuff_packs.set(mystuff_packs)

        self.refresh_profiles()
        self.select_profile()

    def add_mystuff_path(self) -> None:
        """
        Add a new path to the currently selected MyStuff profile
        """

        if (mystuff_path := filedialog.askdirectory(title=_("SELECT_MYSTUFF"), mustexist=True)) is None: return
        mystuff_path = Path(mystuff_path)

        mystuff_packs = self.root.options.mystuff_packs.get()
        mystuff_packs[self.root.options.mystuff_pack_selected.get()]["paths"].append(str(mystuff_path.resolve()))
        self.root.options.mystuff_packs.set(mystuff_packs)

        self.select_profile()

    def remove_mystuff_path(self) -> None:
        """
        Remove the selected MyStuff path from the profile
        """
        
        selections = self.listbox_mystuff_paths.curselection()
        if not selections: return

        mystuff_packs = self.root.options.mystuff_packs.get()
        for selection in selections:
            mystuff_packs[self.root.options.mystuff_pack_selected.get()]["paths"].pop(selection)
        self.root.options.mystuff_packs.set(mystuff_packs)

        self.select_profile()

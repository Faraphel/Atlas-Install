import json
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


class Orderbox(Listbox):
    def order_up(self, *args, **kwargs):
        self.order_change(delta_start=1)

    def order_down(self, *args, **kwargs):
        self.order_change(delta_end=1)

    def order_change(self, delta_start: int = 0, delta_end: int = 0):
        selection = self.curselection()
        if len(selection) < 1: return
        index = selection[0]

        values = self.get(index - delta_start, index + delta_end)
        if len(values) < 2: return

        self.delete(index - delta_start, index + delta_end)
        self.insert(index - delta_start, *reversed(values))

        self.selection_set(index - delta_start + delta_end)


class TrackConfiguration:
    def __init__(self, common):
        self.common = common

        self.root = Toplevel(self.common.gui_main.root)
        self.root.title(self.common.translate("Track configuration"))
        self.root.iconbitmap("./icon.ico")
        self.root.resizable(False, False)
        self.root.grab_set()

        self.text_is_equal_to = self.common.translate("is equal to")
        self.text_is_in = self.common.translate("is in")
        self.text_is_between = self.common.translate("is between")
        self.text_contains = self.common.translate("contains")

        self.text_and = self.common.translate("and")
        self.text_nand = self.common.translate("nand")
        self.text_or = self.common.translate("or")
        self.text_nor = self.common.translate("nor")
        self.text_xor = self.common.translate("xor")
        self.text_xnor = self.common.translate("xnor")
        self.condition_link_end = self.common.translate("end")

        self.condition_links = {
            self.text_and: lambda a, b: lambda track: a(track) and b(track),
            self.text_nand: lambda a, b: lambda track: not (a(track) and b(track)),
            self.text_or: lambda a, b: lambda track: a(track) or b(track),
            self.text_nor: lambda a, b: lambda track: not (a(track) or b(track)),
            self.text_xor: lambda a, b: lambda track: a(track) != b(track),
            self.text_xnor: lambda a, b: lambda track: a(track) == b(track),
            self.condition_link_end: -1
        }

        def get_change_enable_track_filter_func(root: [Frame, LabelFrame], frames_filter: list, variable_enable: BooleanVar):
            def change_enable_track_filter(event: Event = None):
                if variable_enable.get(): self.add_frame_track_filter(root=root, frames_filter=frames_filter)
                else: self.del_frame_track_filter(frames_filter=frames_filter)

            return change_enable_track_filter

        self.track_sort = LabelFrame(self.root, text=self.common.translate("Sort Track"))
        self.track_sort.grid(row=1, column=1, sticky="NEWS")

        Label(self.track_sort, text=self.common.translate("Sort track by"," : ")).grid(row=1, column=1)
        self.combobox_track_sort = ttk.Combobox(
            self.track_sort,
            values=list(self.common.ct_config.get_all_track_possibilities())
        )
        self.combobox_track_sort.grid(row=1, column=2, sticky="NEWS")
        self.combobox_track_sort.insert(END, self.common.ct_config.sort_track_attr)
        self.combobox_track_sort.config(state="readonly")

        self.track_filter = LabelFrame(self.root, text=self.common.translate("Filter Track"))
        self.track_filter.grid(row=2, column=1, sticky="NEWS")

        self.variable_enable_track_filter = BooleanVar(value=False)
        self.frames_track_filter = []
        self.checkbutton_track_filter = ttk.Checkbutton(
            self.track_filter,
            text=self.common.translate("Enable track filter"),
            variable=self.variable_enable_track_filter,
            command=get_change_enable_track_filter_func(
                self.track_filter,
                self.frames_track_filter,
                self.variable_enable_track_filter
            )
        )
        self.checkbutton_track_filter.grid(row=1, column=1)
        Label(
            self.track_filter,
            text=self.common.translate("Warning : only unordered tracks are affected by this option."),
            fg="gray"
        ).grid(row=2, column=1)

        self.track_highlight = LabelFrame(self.root, text="Highlight Track")
        self.track_highlight.grid(row=3, column=1, sticky="NEWS")

        self.variable_enable_track_highlight = BooleanVar(value=False)
        self.frames_track_highlight = []
        self.checkbutton_track_highlight = ttk.Checkbutton(
            self.track_highlight,
            text=self.common.translate("Enable track highlight"),
            variable=self.variable_enable_track_highlight,
            command=get_change_enable_track_filter_func(
                self.track_highlight,
                self.frames_track_highlight,
                self.variable_enable_track_highlight
            )
        )
        self.checkbutton_track_highlight.grid(row=1, column=1)

        self.track_random_new = LabelFrame(self.root, text=self.common.translate("Overwrite random cup new"))
        self.track_random_new.grid(row=4, column=1, sticky="NEWS")

        self.variable_enable_track_random_new = BooleanVar(value=False)
        self.frames_track_random_new = []
        self.checkbutton_track_random_new = ttk.Checkbutton(
            self.track_random_new,
            text=self.common.translate("Enable overwriting random \"new\" track"),
            variable=self.variable_enable_track_random_new,
            command=get_change_enable_track_filter_func(
                self.track_random_new,
                self.frames_track_random_new,
                self.variable_enable_track_random_new
            )
        )
        self.checkbutton_track_random_new.grid(row=1, column=1)

        self.all_frames_filters = {
            "track_filter": {
                "frame": self.track_filter,
                "variable_checkbox": self.variable_enable_track_filter,
                "list": self.frames_track_filter
            },
            "track_highlight": {
                "frame": self.track_highlight,
                "variable_checkbox": self.variable_enable_track_highlight,
                "list": self.frames_track_highlight
            },
            "track_random_new": {
                "frame": self.track_random_new,
                "variable_checkbox": self.variable_enable_track_random_new,
                "list": self.frames_track_random_new
            }
        }

        if self.common.json_frame_filter: self.load_from_json(self.common.json_frame_filter)

        self.frame_action_button = Frame(self.root)
        self.frame_action_button.grid(row=100, column=1, sticky="E")

        Button(
            self.frame_action_button,
            text=self.common.translate("Apply change"),
            relief=RIDGE,
            command=self.apply_configuration
        ).grid(row=1, column=1, sticky="W")

        Button(
            self.frame_action_button,
            text=self.common.translate("Save to file"),
            relief=RIDGE,
            command=self.promp_save_to_file
        ).grid(row=1, column=2, sticky="E")

        Button(
            self.frame_action_button,
            text=self.common.translate("Load from file"),
            relief=RIDGE,
            command=self.promp_load_from_file
        ).grid(row=1, column=3, sticky="E")

    def del_frame_track_filter(self, frames_filter: list, index: int = 0):
        for elem in frames_filter[index:]:  # remove all track filter after this one
            elem["frame"].destroy()
        del frames_filter[index:]

    def add_frame_track_filter(self, root: [Frame, LabelFrame], frames_filter: list):
        index = len(frames_filter) - 1

        frame = Frame(root)
        frame.grid(row=len(frames_filter) + 10, column=1, sticky="NEWS")
        Label(frame, text=self.common.translate("If track's")).grid(row=1, column=1)
        track_property = ttk.Combobox(frame, state="readonly", values=list(self.common.ct_config.get_all_track_possibilities()))
        track_property.current(0)
        track_property.grid(row=1, column=2)

        frame_equal = Frame(frame)
        entry_equal = Entry(frame_equal, width=20)
        entry_equal.grid(row=1, column=1)
        entry_equal.insert(END, self.common.translate("value"))

        frame_in = Frame(frame)
        entry_in = Entry(frame_in, width=30)
        entry_in.grid(row=1, column=1)
        entry_in.insert(END, self.common.translate("value1, value2, ..."))

        frame_between = Frame(frame)
        entry_start = Entry(frame_between, width=10)
        entry_start.grid(row=1, column=1)
        entry_start.insert(END, self.common.translate("value1"))
        Label(frame_between, text=self.common.translate("and")).grid(row=1, column=2)
        entry_end = Entry(frame_between, width=10)
        entry_end.insert(END, self.common.translate("value2"))
        entry_end.grid(row=1, column=3)

        frame_contains = Frame(frame)
        entry_contains = Entry(frame_contains, width=20)
        entry_contains.grid(row=1, column=1)
        entry_contains.insert(END, self.common.translate("value"))

        condition_frames = {
            self.text_is_equal_to: frame_equal,
            self.text_is_in: frame_in,
            self.text_is_between: frame_between,
            self.text_contains: frame_contains,
        }

        def change_condition_type(event: Event = None):
            condition = combobox_condition_type.get()
            for frame in condition_frames.values(): frame.grid_forget()
            condition_frames[condition].grid(row=1, column=10)

        combobox_condition_type = ttk.Combobox(frame, state="readonly", values=list(condition_frames.keys()), width=10)
        combobox_condition_type.current(0)
        combobox_condition_type.bind("<<ComboboxSelected>>", change_condition_type)
        change_condition_type()
        combobox_condition_type.grid(row=1, column=3)

        def change_condition_link(event: Event = None):
            link = next_condition_link.get()

            if link == self.condition_link_end:
                self.del_frame_track_filter(frames_filter, index=index + 1)

            else:
                if frames_filter[-1]["frame"] == frame:  # if this is the last filter available
                    self.add_frame_track_filter(root=root, frames_filter=frames_filter)

        next_condition_link = ttk.Combobox(frame, state="readonly", values=list(self.condition_links.keys()), width=10)
        next_condition_link.bind("<<ComboboxSelected>>", change_condition_link)
        next_condition_link.set(self.condition_link_end)
        next_condition_link.grid(row=1, column=100)

        frames_filter.append({
            "frame": frame,
            "track_property": track_property,
            "condition_type": combobox_condition_type,

            "value_equal": entry_equal,
            "value_in": entry_in,
            "value_between_start": entry_start,
            "value_between_end": entry_end,
            "value_contains": entry_contains,

            "next_condition_link": next_condition_link
        })

    def apply_configuration(self):
        self.common.gui_main.is_track_configuration_edited = True
        self.common.ct_config.sort_track_attr = self.combobox_track_sort.get()

        self.common.ct_config.filter_track_selection = self.get_filter(
            self.variable_enable_track_filter,
            self.frames_track_filter
        )
        self.common.ct_config.filter_track_highlight = self.get_filter(
            self.variable_enable_track_highlight,
            self.frames_track_highlight
        )
        self.common.ct_config.filter_track_random_new = self.get_filter(
            self.variable_enable_track_random_new,
            self.frames_track_random_new
        )

        self.common.json_frame_filter = self.save_to_json()
        self.root.destroy()

    def get_filter(self, condition_enabled: BooleanVar, frames_filter: list):
        s = lambda x: str(x).strip()

        filter_condition = lambda track: True
        if not condition_enabled.get(): return filter_condition
        next_condition_link_func = lambda a, b: lambda track: a(track) and b(track)

        for frame_filter in frames_filter:
            track_property = frame_filter["track_property"].get()

            value_equal = frame_filter["value_equal"].get()
            value_in = frame_filter["value_in"].get()
            value_contains = frame_filter["value_contains"].get()
            value_between_start = frame_filter["value_between_start"].get()
            value_between_end = frame_filter["value_between_end"].get()

            def _is_between_func_wrapper(property):
                def _is_between_func(track):
                    from_ = s(value_between_start)
                    to = s(value_between_end)
                    prop = s(getattr(track, property, None))

                    if from_.isnumeric() and prop.isnumeric() and to.isnumeric(): return int(from_) <= int(prop) <= int(to)
                    else: return from_ <= prop <= to

                return _is_between_func

            track_conditions_filter = {
                self.text_is_equal_to: lambda property: lambda track:
                    s(getattr(track, property, None)) == s(value_equal),
                self.text_is_in: lambda property: lambda track:
                    s(getattr(track, property, None)) in [s(v) for v in value_in.split(",")],
                self.text_is_between:
                    _is_between_func_wrapper,
                self.text_contains: lambda property: lambda track:
                    s(value_contains) in s(getattr(track, property, None))
            }

            track_condition_type = frame_filter["condition_type"].get()
            track_condition_filter = track_conditions_filter[track_condition_type]

            filter_condition = next_condition_link_func(
                filter_condition,
                track_condition_filter(track_property)
            )
            next_condition_link = frame_filter["next_condition_link"].get()
            next_condition_link_func = self.condition_links[next_condition_link]

        return filter_condition

    def save_to_json(self) -> dict:
        """
        save the menu values in a dictionnary
        :return: dictionnary
        """

        json_frame_filter = {}

        for frame_name, tk_frames_data in self.all_frames_filters.items():
            json_frame_filter[frame_name] = []

            for tk_data in tk_frames_data["list"]:
                json_frame_filter[frame_name].append({})

                for varname, tkvar in tk_data.items():
                        if "get" in dir(tkvar):
                            json_frame_filter[frame_name][-1][varname] = tkvar.get()

        return json_frame_filter

    def save_to_file(self, path: str):
        with open(path, "w", encoding="utf8") as f:
            json.dump(self.save_to_json(), f, ensure_ascii=False)

    def promp_save_to_file(self):
        filename = filedialog.asksaveasfilename(
            title=self.common.translate("Save track configuration"),
            defaultextension=".mkwf.tc",
            filetypes=[(self.common.translate("track configuration"), "*.mkwf.tc")]
        )
        if filename: self.save_to_file(filename)

    def load_from_json(self, json_frame_filter: dict) -> None:
        """
        :param json_frame_filter: json to load in the menu
        """

        for json_filter_name, json_frames in json_frame_filter.items():

            tk_frame_filter = self.all_frames_filters[json_filter_name]
            self.del_frame_track_filter(tk_frame_filter["list"])
            tk_frame_filter["variable_checkbox"].set(len(json_frames) > 0)

            for i, json_frame in enumerate(json_frames):
                self.add_frame_track_filter(
                    self.all_frames_filters[json_filter_name]["frame"],
                    self.all_frames_filters[json_filter_name]["list"]
                )

                for json_param_name, json_param_value in json_frame.items():
                    obj = self.all_frames_filters[json_filter_name]["list"][i][json_param_name]
                    if type(obj) in [Entry]:
                        obj.delete(0, END)
                        obj.insert(0, json_param_value)
                    else:
                        obj.set(json_param_value)

    def load_from_file(self, path: str) -> None:
        with open(path, encoding="utf8") as f:
            self.load_from_json(json.load(f))

    def promp_load_from_file(self):
        filename = filedialog.askopenfilename(
            title=self.common.translate("Load track configuration"),
            defaultextension=".mkwf.tc",
            filetypes=[(self.common.translate("track configuration"), "*.mkwf.tc")]
        )
        if filename: self.load_from_file(filename)
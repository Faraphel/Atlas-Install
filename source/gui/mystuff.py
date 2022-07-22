import tkinter
from tkinter import ttk


class Window(tkinter.Toplevel):
    def __init__(self):
        super().__init__()

        self.grab_set()

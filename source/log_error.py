import traceback
from tkinter import messagebox


def log_error(self):
    error = traceback.format_exc()
    with open("./error.log", "a") as f: f.write(f"---\n{error}\n")
    messagebox.showerror(self.translate("Error"), self.translate("An error occured", " :", "\n", error, "\n\n"))
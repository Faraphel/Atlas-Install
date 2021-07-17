import traceback


def log_error(func):
    try: func()
    except Exception:
        error = traceback.format_exc()
        with open("./error.log", "a") as f: f.write(f"---\n{error}\n")
        # messagebox.showerror(self.translate("Error"), self.translate("An error occured", " :", "\n", error, "\n\n"))
import traceback

def log_error(self, exception):
    with open("error.log", "a") as f: f.write(f"---\n{traceback.format_exc()}\n")

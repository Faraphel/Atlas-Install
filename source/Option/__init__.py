class Option:
    def __init__(self):
        self.language = "en"
        self.format = "FST"
        self.disable_download = False
        self.del_track_after_conv = False
        self.dont_check_for_update = False
        self.dont_check_track_sha1 = False
        self.process_track = 8

    from .edit import edit
    from .load_from_file import load_from_file
    from .load_from_json import load_from_json
    from .save_to_file import save_to_file

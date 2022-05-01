from tkinter import messagebox
import traceback
import os


class RomAlreadyPatched(Exception):
    def __init__(self):
        super().__init__("ROM Already patched !")


class InvalidGamePath(Exception):
    def __init__(self):
        super().__init__("This path is not valid !")


class InvalidFormat(Exception):
    def __init__(self):
        super().__init__("This game format is not supported !")


class TooMuchSha1CheckFailed(Exception):
    def __init__(self):
        super().__init__("Too much sha1 check failed !")


class CantDownloadTrack(Exception):
    def __init__(self, track, http_error: [str, int]):
        super().__init__(f"Can't download track {track.name} ({track.sha1}) (error {http_error}) !")


class CantConvertTrack(Exception):
    def __init__(self):
        super().__init__("Can't convert track.")


class MissingTrackWU8(Exception):
    def __init__(self):
        super().__init__("The original wu8 track file is missing !")


class CorruptedPack(Exception):
    def __init__(self):
        super().__init__("This pack seem corrupted !")


class ErrorLogger:
    def __init__(self, common):
        self.common = common

    def log_error(self) -> None:
        """
        When an error occur, will show it in a messagebox and write it in error.log
        """
        error = traceback.format_exc()
        file_list = os.listdir('./file/') if os.path.exists("./file/") else None
        ctconfig_list = os.listdir(self.common.ct_config.pack_path) if os.path.exists(self.common.ct_config.pack_path) else None

        with open("./error.log", "a") as f:
            f.write(
                f"---\n"
                f"For game version : {self.common.ct_config.version}\n"
                f"./file/ directory : {file_list}\n"
                f"ctconfig directory : {ctconfig_list}\n"
                f"GAME/files/ information : {self.common.game.path, self.common.game.region}\n"
                f"{error}\n"
            )

        messagebox.showerror(
            self.common.translate("Error"),
            self.common.translate("An error occured", " :", "\n", error, "\n\n")
        )

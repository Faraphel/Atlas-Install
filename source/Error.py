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

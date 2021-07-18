class InvalidGamePath(Exception):
    def __init__(self):
        super().__init__("This path is not valid !")


class InvalidFormat(Exception):
    def __init__(self):
        super().__init__("This game format is not supported !")


class TooMuchDownloadFailed(Exception):
    def __init__(self):
        super().__init__("Too much download failed !")


class TooMuchSha1CheckFailed(Exception):
    def __init__(self):
        super().__init__("Too much sha1 check failed !")


class CantConvertTrack(Exception):
    def __init__(self):
        super().__init__("Can't convert track, check if download are enabled.")
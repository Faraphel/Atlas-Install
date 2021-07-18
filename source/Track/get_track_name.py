def get_track_name(self):
    prefix = self.prefix + " " if self.prefix else ""
    suffix = self.suffix + " " if self.suffix else ""

    name = (prefix + self.name + suffix)
    return name

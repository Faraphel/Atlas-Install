import source.wszst


def check_sha1(self):
    if source.wszst.sha1(self.file_wu8) == self.sha1:
        return 0
    else:
        return -1

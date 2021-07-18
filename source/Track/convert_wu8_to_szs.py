import source.wszst


def convert_wu8_to_szs(self):
    return source.wszst.normalize(src_file=self.file_wu8, use_popen=True)

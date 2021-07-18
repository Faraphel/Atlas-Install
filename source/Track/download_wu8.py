from ..definition import *

import requests
import os


def download_wu8(self):
    returncode = 0

    dl = requests.get(get_github_content_root(self) + self.file_wu8, allow_redirects=True, stream=True)
    if os.path.exists(self.file_wu8):
        if int(dl.headers['Content-Length']) == os.path.getsize(self.file_wu8):
            return 1
        else:
            returncode = 3

    if dl.status_code == 200:  # if page is found
        with open(self.file_wu8, "wb") as file:
            chunk_size = 4096
            for i, chunk in enumerate(dl.iter_content(chunk_size=chunk_size)):
                file.write(chunk)
                file.flush()
        return returncode
    else:
        print(f"error {dl.status_code} {self.file_wu8}")
        return -1

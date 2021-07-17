import requests
import os

from .definition import *


def get_github_file(self, file):
    try:
        returncode = 0
        if self.boolvar_disable_download.get(): return 2

        dl = requests.get(get_github_content_root(self)+file, allow_redirects=True, stream=True)
        if os.path.exists(file):
            if int(dl.headers['Content-Length']) == os.path.getsize(file): return 1
            else: returncode = 3

        if dl.status_code == 200:  # if page is found
            with open(file, "wb") as file:
                chunk_size = 4096
                for i, chunk in enumerate(dl.iter_content(chunk_size=chunk_size)):
                    file.write(chunk)
                    file.flush()
            return returncode
        else:
            print(f"error {dl.status_code} {file}")
            return -1
    except:
        self.log_error()
        return -1

# TODO: if version > github version, do not search in master branch but dev branch

import requests
import subprocess
import os

from .definition import *


def get_github_file(self, file):
    try:
        returncode = 0
        if self.boolvar_disable_download.get(): return 2

        dl = requests.get(GITHUB_CONTENT_ROOT+file, allow_redirects=True, stream=True)
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


def check_track_sha1(self, file, excepted_sha1):
    sha1 = subprocess.run(["./tools/szs/wszst", "SHA1", file, "--autoadd-path", "./file/auto-add/"],
                          check=True, creationflags=CREATE_NO_WINDOW,
                          stdout=subprocess.PIPE).stdout.decode().split(" ")[0]
    if excepted_sha1 == sha1: return 0
    else: return -1

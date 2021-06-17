import requests
import os

root = "https://raw.githubusercontent.com/Faraphel/MKWF-Install/master/"


def get_github_file(self, file):
    try:
        dl = requests.get(root+file, allow_redirects=True, stream=True)
        if os.path.exists(file):
            if int(dl.headers['Content-Length']) == os.path.getsize(file):
                return 1

        if dl.status_code == 200:  # if page is found
            with open(file, "wb") as file:
                chunk_size = 4096
                for i, chunk in enumerate(dl.iter_content(chunk_size=chunk_size)):
                    file.write(chunk)
                    file.flush()
            return 0
        else:
            print(f"error {dl.status_code} {file}")
            return -1
    except:
        self.log_error()
        return -1

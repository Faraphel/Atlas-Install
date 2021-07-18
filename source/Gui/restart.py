import subprocess
import sys
import os

from source.definition import *


def restart():
    subprocess.Popen([sys.executable] + sys.argv, creationflags=CREATE_NO_WINDOW, cwd=os.getcwd())
    exit()

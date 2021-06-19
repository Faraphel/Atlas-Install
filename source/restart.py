import subprocess
import sys
import os

from .definition import *


def restart(self):
    subprocess.Popen([sys.executable] + sys.argv, creationflags=CREATE_NO_WINDOW, cwd=os.getcwd())
    sys.exit()
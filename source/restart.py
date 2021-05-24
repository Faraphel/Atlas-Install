import sys
import os


def restart(self):
    os.execl(sys.executable, f'"{sys.executable}"', *sys.argv)
    sys.exit()
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from threading import Thread
import subprocess
import requests
import zipfile
import shutil
import json
import glob
import os

from source.definition import *
from source.check_update import *

class ClassApp():
    from source.__init__ import __init__
    from source.Progress import Progress
    from source.StateButton import StateButton
    from source.create_lecode_config import create_lecode_config
    from source.patch_file import patch_file
    from source.install_mod import install_mod


# TODO: Langue
# TODO: Split Code into multiple file
App = ClassApp()
mainloop()
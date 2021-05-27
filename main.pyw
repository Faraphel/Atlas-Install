from tkinter import *
from PIL import Image, ImageFont, ImageDraw
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

class ClassApp():
    from source.__init__ import __init__
    from source.translate import translate, change_language, get_language
    from source.Progress import Progress
    from source.check_update import check_update
    from source.StateButton import StateButton
    from source.create_lecode_config import create_lecode_config
    from source.patch_file import patch_file
    from source.patch_bmg import patch_bmg
    from source.install_mod import install_mod
    from source.restart import restart
    from source.patch_img_desc import patch_img_desc
    from source.patch_ct_icon import patch_ct_icon


# TODO: Wiki Github
App = ClassApp()
App.root.mainloop()
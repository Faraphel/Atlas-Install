from tkinter import *
from PIL import Image, ImageFont, ImageDraw
from tkinter import messagebox, filedialog, ttk
from threading import Thread
import subprocess
import traceback
import requests
import zipfile
import shutil
import json
import glob
import math
import os

from source.definition import *

class ClassApp():
    from source.__init__ import __init__
    from source.translate import translate
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
    from source.log_error import log_error
    from source.get_github_file import get_github_file, check_track_sha1
    from source.patch_track import load_ct_config, patch_track, patch_autoadd, get_trackctname, get_trackname
    from source.patch_image import patch_image
    from source.option import load_option, change_option


App = ClassApp()
App.root.mainloop()
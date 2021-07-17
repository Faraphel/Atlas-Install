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
    from source.patch_file import patch_file
    from source.patch_bmg import patch_bmg
    from source.restart import restart
    from source.patch_img_desc import patch_img_desc
    from source.log_error import log_error
    from source.patch_track import patch_track
    from source.patch_image import patch_image

    from source.Option import Option
    from source.CT_Config import CT_Config
    from source.Game import Game, InvalidGamePath, InvalidFormat


App = ClassApp()
App.root.mainloop()
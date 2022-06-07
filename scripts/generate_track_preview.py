"""
this script allow you to more easily select map preview for each track.
"""
import shutil

import requests
from selenium import webdriver
import keyboard
import ctypes
import time
import glob
import os

get_filename = lambda file: ".".join(file.split(".")[:-1])
get_nodir = lambda file: file.replace("\\", "/").split("/")[-1]
move_cursor_to = ctypes.windll.user32.SetCursorPos
os.makedirs("./map preview/tmp/", exist_ok=True)

chrome_option = webdriver.ChromeOptions()
driver = webdriver.Chrome("./map preview/chromedriver.exe", options=chrome_option)
driver.get("https://noclip.website/")


LAST_TRACK_PLAYED = "d97a4b29d422e830e07e98196e4f2e3f41a90086"
latest_track_passed = LAST_TRACK_PLAYED is None
tracks = glob.iglob("../file/Track/*.szs")
track = "none.png"


def ignore_track():
    global track, driver
    print("skipping to next track")

    driver.close()
    driver = webdriver.Chrome("./map preview/chromedriver.exe", options=chrome_option)
    driver.get("https://noclip.website/")

    skip_to_next()


def save_screenshot():
    global track
    print("saving screenshot")
    driver.save_screenshot(filename=f"./map preview/image/{get_filename(get_nodir(track))}.png")
    skip_to_next()


def skip_to_next():
    global track, latest_track_passed

    if os.path.exists("./map preview/tmp/" + get_nodir(track)):
        os.remove("./map preview/tmp/" + get_nodir(track))

    track = next(tracks)

    while True:
        sha1 = get_nodir(track).replace(".szs", "")
        if not latest_track_passed and sha1 != LAST_TRACK_PLAYED:
            track = next(tracks)
            continue

        else: latest_track_passed = True

        if requests.get(f"https://github.com/Faraphel/MKWF-Install/raw/track-preview/map/{sha1}.png").status_code != 200: break
        print(f"track {sha1} already exist !")
        track = next(tracks)

    print(track)

    shutil.copy(track, f"./map preview/tmp/{get_nodir(track)}")


skip_to_next()
keyboard.add_hotkey('h', save_screenshot)
keyboard.add_hotkey('j', ignore_track)

while True:
    time.sleep(1)

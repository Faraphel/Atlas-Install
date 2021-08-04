"""
this script allow you to more easily select map preview for each track.
"""

from selenium import webdriver
import keyboard
import shutil
import ctypes
import time
import glob
import os

get_filename = lambda file: ".".join(file.split(".")[:-1])
get_nodir = lambda file: file.replace("\\", "/").split("/")[-1]
move_cursor_to = ctypes.windll.user32.SetCursorPos

chrome_option = webdriver.ChromeOptions()
driver = webdriver.Chrome("./map preview/chromedriver.exe", options=chrome_option)
driver.get("https://noclip.website/")
driver.fullscreen_window()
time.sleep(5)

driver.execute_script("var element = arguments[0]; element.parentNode.removeChild(element);",
                      driver.find_element_by_id("Panel"))

tracks = glob.iglob("../file/Track/*.szs")
track = next(tracks)
shutil.copy(track, "./map preview/tmp/" + get_nodir(track))


def save_screenshot():
    global track
    driver.save_screenshot(filename=f"./map preview/image/{get_filename(get_nodir(track))}.png")
    skip_to_next()


def skip_to_next():
    global track
    os.remove("./map preview/tmp/" + get_nodir(track))

    track = next(tracks)
    while os.path.exists(f"./map preview/image/{get_filename(get_nodir(track))}.png"):
        track = next(tracks)

    shutil.copy(track, "./map preview/tmp/" + get_nodir(track))


keyboard.add_hotkey('h', save_screenshot)

while True:
    time.sleep(1)

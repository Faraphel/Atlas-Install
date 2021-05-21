from cx_Freeze import setup, Executable
import sys
import glob

include_files = [
    "./icon.ico",
    "./LICENSE",
    "./README.md",
    "./version",
    "./convert_file.json",
    "./fs.json",

    "./tools",

    ("./file/Track-WU8","./file/Track-WU8"),
    ("./file/video.thp","./file/video.thp"),
    ("./file/Back.brctr","./file/Back.brctr"),
    ("./file/cup_icon_64x64_common.brlyt","./file/cup_icon_64x64_common.brlyt"),
    ("./file/CupSelectCup.brctr","./file/CupSelectCup.brctr"),
    ("./file/CourseSelectCup.brctr","./file/CourseSelectCup.brctr"),
    ("./file/course_name.brlyt","./file/course_name.brlyt"),
    ("./file/lecode-PAL.bin","./file/lecode-PAL.bin"),
    ("./file/itemBoxNiseRtpa.brres","./file/itemBoxNiseRtpa.brres"),
    ("./file/RKRace.breff","./file/RKRace.breff"),
    sys.exec_prefix + "\\DLLs\\tcl86t.dll",
    sys.exec_prefix + "\\DLLs\\tk86t.dll",
]

include_files.extend([("./file/"+x, "./file/"+x) for x in glob.glob("./file/*.txt")])
include_files.extend([("./file/"+x, "./file/"+x) for x in glob.glob("./file/*.png")])


options = {
    "build_exe":{
        "include_files": include_files,
        "includes": ["tkinter", "requests"],
        "packages": [],
        "excludes": []
    }
}

setup(
    options=options,
    name='MKWF-Install',
    version='0.1',
    url='https://github.com/Faraphel/MKWF-Install',
    license='Apache-2.0',
    author='Faraphel',
    author_email='rc60650@hotmail.com',
    description='Installateur pour Mario Kart Wii Faraphel.',
    executables = [Executable("./main.pyw",
                              icon = "./icon.ico",
                              base = "win32gui",
                              target_name = "MKWF-Install.exe",
                              shortcut_name = "MKWF-Install",
                              shortcut_dir = "DesktopFolder")],
)
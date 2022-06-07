from cx_Freeze import setup, Executable
import sys
import json

include_files = [
    "./icon.ico",
    "./LICENSE",
    "./README.md",
    "./version",
    "./translation.json",

    "./assets",
    "./tools",

    sys.exec_prefix + "\\DLLs\\tcl86t.dll",
    sys.exec_prefix + "\\DLLs\\tk86t.dll",
]

options = {
    "build_exe": {
        "include_files": include_files,
        "includes": ["tkinter", "requests", "PIL", "distutils"],
        "include_msvcr": True,
        "packages": ["tkinter", "distutils"],
    }
}

with open("./version") as f:
    version = json.load(f)

setup(
    options=options,
    name='MKWF-Install',
    version=version["version"],
    url='https://github.com/Faraphel/MKWF-Install',
    license='Apache-2.0',
    author='Faraphel',
    author_email='rc60650@hotmail.com',
    description='Mario Kart Wii Mod Installer.',
    executables=[
        Executable(
            "./main.pyw",
            icon="./icon.ico",
            base="win32gui",
            target_name="MKWF-Install.exe",
            shortcut_name="MKWF-Install",
            shortcut_dir="DesktopFolder"
        )
    ],
)

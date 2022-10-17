from cx_Freeze import setup, Executable
import sys
import source

include_files = [
    "./LICENSE.md",
    "./README.md",

    "./assets",
    "./tools",

    sys.exec_prefix + "\\DLLs\\tcl86t.dll",
    sys.exec_prefix + "\\DLLs\\tk86t.dll",
]

options = {
    "build_exe": {
        "include_files": include_files,
        "includes": ["tkinter", "PIL"],
        "include_msvcr": True,
        "packages": ["tkinter"],
    }
}

setup(
    options=options,
    name='MKWF-Install',
    version=".".join(source.__version__),
    url='https://github.com/Faraphel/MKWF-Install',
    license='Apache-2.0',
    author='Faraphel',
    author_email='rc60650@hotmail.com',
    description='Mario Kart Wii Mod Installer.',
    executables=[
        Executable(
            "./main.pyw",
            icon="./assets/icon.ico",
            base="win32gui",
            target_name="MKWF-Install.exe",
            shortcut_name="MKWF-Install",
            shortcut_dir="DesktopFolder"
        )
    ],
)

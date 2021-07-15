from cx_Freeze import setup, Executable

options = {
    "build_exe":{
        "includes": ["requests"],
        "packages": [],
        "excludes": []
    }
}

setup(
    options=options,
    name='MKWF-Install',
    version='0.3',
    url='https://github.com/Faraphel/MKWF-Install',
    license='GPL-3.0',
    author='Faraphel',
    author_email='rc60650@hotmail.com',
    description='MKWF-Install Updater.',
    executables = [Executable("./Updater.py",
                              target_name = "Updater.exe",
                              shortcut_name = "MKWF-Install Updater",
                              shortcut_dir = "DesktopFolder")],
)
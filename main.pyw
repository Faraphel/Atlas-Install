from source.gui import install
from source.option import Options
from source.translation import load_language


# this allows every variable to be accessible from other files, useful for the plugins
self = __import__(__name__)

options = Options.from_file("./option.json")
translater = load_language(options.language.get())

self.window = install.Window(options)
self.window.run()

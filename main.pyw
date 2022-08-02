from source.gui import install
from source.option import Option
from source.translation import load_language


# this allows every variable to be accessible from other files, useful for the plugins
self = __import__(__name__)

options = Option.from_file("./option.json")
translater = load_language(options["language"])

self.window = install.Window(options)
self.window.run()

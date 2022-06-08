from source.gui import install
import sys

# this allows every variable to be accessible from other files, useful for the plugins
self = sys.modules[__name__]

self.window = install.Window()
self.window.run()

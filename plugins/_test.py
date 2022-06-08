from source import event
import tkinter
import sys


@event.on("source.gui.install.Window.run_after")
def test_button():
    """
    Test function for the plugins
    :return:
    """

    # get the main window from the main module
    window = sys.modules["__main__"].window

    # get the install button from the main window
    window.button_install.config(text="installation plugins")

    # add a custom button on the main window
    tkinter.Button(window, text="test des plugins", command=lambda: print("test")).grid(
        row=10, column=1, sticky="nsew"
    )
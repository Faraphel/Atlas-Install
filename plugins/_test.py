from source import event
import tkinter


@event.on("source.gui.install.Window.__init__")
def test_button(master):
    tkinter.Button(master, text="test des plugins", command=lambda: print("test")).grid(
        row=10, column=1, sticky="nsew"
    )
    print("I have been called")

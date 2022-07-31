import tkinter
from abc import abstractmethod, ABC
from typing import Type


ModConfig: any


class InvalidPreviewWindowName(Exception):
    def __init__(self, name: str):
        super().__init__(f"Error : Type of preview window '{name}' not found.")


class AbstractPreviewWindow(tkinter.Toplevel, ABC):
    """
    Represent a window that allow a preview of the result of a value that can be in a settings entry
    """

    name: str

    @abstractmethod
    def __init__(self, mod_config: "ModConfig", template_variable: tkinter.StringVar = None):
        super().__init__()
        ...

    @classmethod
    def get(cls, name: str) -> Type["AbstractPreviewWindow"]:
        """
        Return the windows class object from its name
        :param name: name of the window class
        :return: the window class object
        """
        for subclass in filter(lambda subclass: subclass.name == name, cls.__subclasses__()):
            return subclass
        raise InvalidPreviewWindowName(name)


from source.gui.preview import track_formatting, track_selecting

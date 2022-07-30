from abc import ABC, abstractmethod


class AbstractTypeSettings(ABC):
    type: str  # type name of the settings
    value: str  # value for the settings

    @abstractmethod
    def tkinter_show(self, master) -> None:
        """
        Show the option inside a tkinter widget
        """
        ...


from source.mkw.ModSettings.TypeSettings import String, Choices

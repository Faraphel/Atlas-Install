from types import FunctionType
from pathlib import Path
import sys

# using this self variable allow us to keep the events in the whole module
self = sys.modules[__name__]
self.events = {}


def on(event_name: str):
    """
    Register the function to be called when the event is called.
    :param event_name: name of the event
    :return: decorator
    """

    def decorator(func: FunctionType):
        if event_name not in self.events: self.events[event_name] = []
        self.events[event_name].append(func)

        return func

    return decorator


def register(func: FunctionType):
    """
    Register the function as an event.
    :param func: function to register
    :return: function with event call at the end
    """

    def wrapper(*args, **kwargs) -> any:
        return_values = func(*args, **kwargs)
        call_event(f"{func.__module__}.{func.__qualname__}", return_values)
        return return_values

    return wrapper


def call_event(event_name: str, *args, **kwargs) -> None:
    """
    Call all the events associated with the event_name.
    :param event_name: name of the event
    :return:
    """
    for func in self.events.get(event_name, []):
        func()


def initialise_plugins() -> None:
    """
    Execute all the scripts in the ./plugins/ directory that don't start with an underscore.
    :return:
    """
    for file in Path("./plugins/").rglob("[!_]*.py"):
        exec(file.read_text(encoding="utf8"), globals())

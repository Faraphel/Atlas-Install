from dataclasses import dataclass


@dataclass
class Progress:
    """
    Represent the level of progression of the installer. Used for progress bar.
    """

    # this represents the first progress bar, showing every big part in the process
    title: str = None
    part: int = None
    set_part: int = None
    max_part: int = None

    # this represents the second progress bar, showing every step of the current part of the process
    description: str = None
    step: int = None
    set_step: int = None
    max_step: int = None
    determinate: bool = None

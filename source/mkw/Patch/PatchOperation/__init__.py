from source.mkw.Patch import *
from source.mkw.Patch.PatchOperation.Operation import *


class PatchOperation:
    """
    Represent an operation that can be applied onto a patch to modify it before installing
    """

    def __new__(cls, name) -> "Operation":
        """
        Return an operation from its name
        :return: an Operation from its name
        """

        for subclass in filter(lambda subclass: subclass.type == name, AbstractOperation.__subclasses__()):
            return subclass
        raise InvalidPatchOperation(name)

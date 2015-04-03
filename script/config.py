"""Configuration parsing module, which generate a python namespace"""

__all__ = ("Config")

from collections import Mapping, Sequence

class Config(object):
    """A dict subclass that exposes its items as attributes.

    Warning: Namespace instances do not have direct access to the
    dict methods.

    """

    def __init__(self, configFile):
        for line in open(configFile,"r"):
            parts = line.split("=",1)
            if len(parts) > 1:
                try:
                    numVal = int(float(parts[1]))
                    setattr(self,parts[0],numVal)
                except:
                    setattr(self,parts[0],parts[1])
    __hash__ = None

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def __contains__(self, key):
        return key in self.__dict__

from . import core
from . import common
from . import lis
from . import dlis

try:
    import importlib
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:  #check that is the correct error by spoiling something
    pass

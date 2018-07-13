import glob
import os
__all__ = [os.path.basename(x)[:-3] for x in glob.glob("modules/*.py") if not (x.find("_")+1)]
found_modules = __all__[:]
__all__.append("found_modules")

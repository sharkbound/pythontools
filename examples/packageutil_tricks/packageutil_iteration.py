from pkgutil import iter_modules
from icecream import ic

for loader, pkg, ispkg in iter_modules(['.']):
    ic(loader, pkg, ispkg)
    ic(vars(loader))

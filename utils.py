import importlib


def getClassesFromModule(moduleName):
    module = importlib.import_module(moduleName)
    # Get a list of all classes in the module
    return [cls for _, cls in module.__dict__.items() if isinstance(cls, type)]


def getAllClassesNameFrom(moduleName):
    classes = getClassesFromModule(moduleName)
    return [cls.__name__ for cls in classes]


def instantiateClass(moduleName, className):
    classes = getClassesFromModule(moduleName)
    for cls in classes:
        if className == cls.__name__:
            return cls

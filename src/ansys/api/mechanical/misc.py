import typing

class remote_method:
    """Decorator for passing remote methods."""

    def __init__(self, func):
        """Initialize with the given function."""
        self._func = func

    def __call__(self, *args, **kwargs):
        """Call the stored function with provided arguments."""
        return self._func(*args, **kwargs)

    def __call_method__(self, instance, *args, **kwargs):
        """Call the stored function with the instance and provided arguments."""
        return self._func(instance, *args, **kwargs)

    def __get__(self, obj, objtype):
        """Return a partially applied method."""
        from functools import partial

        func = partial(self.__call_method__, obj)
        func._is_remote = True
        func.__name__ = self._func.__name__
        func._owner = obj
        return func


class MethodType:
    """Enum for method or property types."""

    METHOD = 0
    PROP = 1


def try_get_remote_method(
    methodname: str, obj: typing.Any
) -> typing.Tuple[str, typing.Callable]:
    """Try to get a remote method."""
    method = getattr(obj, methodname)
    if not callable(method):
        return None
    if hasattr(method, "_is_remote") and method._is_remote is True:
        return (methodname, method)


def try_get_remote_property(
    attrname: str, obj: typing.Any
) -> typing.Tuple[str, property]:
    """Try to get a remote property."""
    objclass: typing.Type = obj.__class__
    class_attribute = getattr(objclass, attrname)
    getmethod = None
    setmethod = None

    if class_attribute.fget:
        if isinstance(class_attribute.fget, remote_method):
            getmethod = class_attribute.fget
            getmethod._owner = obj
    if class_attribute.fset:
        if isinstance(class_attribute.fset, remote_method):
            setmethod = class_attribute.fset
            setmethod._owner = obj

    return (attrname, property(getmethod, setmethod))


def get_remote_methods(
    obj,
) -> typing.Generator[typing.Tuple[str, typing.Callable, MethodType], None, None]:
    """Yield names and methods of an object's remote methods.

    A remote method is identified by the presence of an attribute `_is_remote` set to `True`.

    Parameters
    ----------
    obj: Any
        The object to inspect for remote methods.

    Yields
    ------
    Generator[Tuple[str, Callable], None, None]
        A tuple containing the method name and the method itself
        for each remote method found in the object
    """
    objclass = obj.__class__
    for attrname in dir(obj):
        if attrname.startswith("__"):
            continue
        if hasattr(objclass, attrname):
            class_attribute = getattr(objclass, attrname)
            if isinstance(class_attribute, property):
                attrname, prop = try_get_remote_property(attrname, obj)
                yield attrname, prop, MethodType.PROP
                continue
        result = try_get_remote_method(attrname, obj)
        if result != None:
            attrname, method = result
            yield attrname, method, MethodType.METHOD

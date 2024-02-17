from typing import TypeVar, cast

from rpyc.core.protocol import DEFAULT_CONFIG

T = TypeVar("T")
safe_attrs = cast(set[str], DEFAULT_CONFIG.get("safe_attrs"))


def safe(attrs: set[str]):
    """
    Alternative to rpyc.exposed/rpyc.service combination,
    which works based on _rpyc_getattr instead of the exposed_ prefix.
    """

    def getter(self, name):
        if name in attrs or name in safe_attrs:
            return getattr(self, name)
        raise AttributeError("access denied")

    def wrapper(cls: type[T]) -> type[T]:
        setattr(cls, "_rpyc_getattr", getter)
        return cls

    return wrapper


def patch_get_methods():
    """
    Monkey-patch rpyc get_methods according to https://github.com/tomerfiliba-org/rpyc/issues/326.
    """

    import inspect

    def getdoc(*args, **kwargs):
        return None

    inspect.getdoc = getdoc


patch_get_methods()

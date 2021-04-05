import importlib.util
import inspect
import os
import sys
from typing import Dict, Type

from updatechecker import checker

_CHECKERS = {}
_LOADED = False

CheckerType = Type[checker.BaseUpdateChecker]


def _is_subclass(sub, parent) -> bool:
    return inspect.isclass(sub) and issubclass(sub, parent)


def _load_checkers(directory: str = None) -> Dict[str, CheckerType]:
    if not directory:
        directory = os.path.dirname(os.path.realpath(__file__))

    modules = {
        filename
        for filename in os.listdir(directory)
        if filename.endswith(".py") and filename != "__init__.py"
    }

    checkers = {}

    for module in modules:
        module_path = os.path.join(directory, module)
        module_name = os.path.splitext(module)[0]

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        checker_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker_module)

        module_contents = [
            getattr(checker_module, module_item) for module_item in dir(checker_module)
        ]

        module_checkers = {
            checker_class.short_name: checker_class
            for checker_class in module_contents
            if _is_subclass(checker_class, checker.BaseUpdateChecker)
        }

        checkers.update(module_checkers)

    return checkers


if not _LOADED:
    _CHECKERS = _load_checkers()


def all_checkers() -> Dict[str, CheckerType]:
    """
    Provides a mapping of all known update checkers.

    This will return all known subclasses of :py:class:`updatechecker.checker.BaseUpdateChecker`
    whether they are known due to being included in this package or to being registered
    using :py:func:`register_checker`.

    :returns: A mapping of all update checker short names to the update checker
    """

    return dict(_CHECKERS)


def register_checker(cls: CheckerType) -> CheckerType:
    """
    Register a class an update checker.

    The given class must specialize :py:class:`updatechecker.checker.BaseUpdateChecker`.

    :param cls: The class to register as an update checker
    :returns: The same class passed as a parameter
    """
    if not issubclass(cls, checker.BaseUpdateChecker):
        raise TypeError("Checkers must be a BaseUpdateChecker")
    _CHECKERS[cls.short_name] = cls
    return cls

import importlib.util
import inspect
import os
import sys
from typing import Type

from updatechecker import checker

_CHECKERS = {}
_LOADED = False


def _is_subclass(sub, parent):
    return inspect.isclass(sub) and issubclass(sub, parent)


def _load_checkers(directory=None):
    if not directory:
        directory = os.path.dirname(os.path.realpath(__file__))

    modules = {
        filename for filename in os.listdir(directory)
        if filename.endswith('.py') and filename != '__init__.py'
    }

    checkers = {}

    for module in modules:
        module_path = os.path.join(directory, module)
        module_name = os.path.splitext(module)[0]

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        checker_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker_module)
    
        module_contents = [
            getattr(checker_module, module_item)
            for module_item in dir(checker_module)
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


def all_checkers():
    return dict(_CHECKERS)


def register_checker(cls):
    if not issubclass(cls, checker.BaseUpdateChecker):
        raise TypeError("Checkers must be a BaseUpdateChecker")
    _CHECKERS[cls.short_name] = cls
    return cls

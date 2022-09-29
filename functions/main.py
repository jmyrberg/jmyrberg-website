"""Module for index."""


import importlib
import os
import sys

from pathlib import Path

# TODO: Add "Access-Control-Origin" properly to all basic functions
# TODO: Add generic way to use request decorator - maybe at deployment stage?


def index(request):
    """This function is just a proxy to other functions."""
    try:
        target = request.path[1:]
        source = Path(__file__).parent / target / 'main.py'
        spec = importlib.util.spec_from_file_location('main', source)
        source_module = importlib.util.module_from_spec(spec)
        sys.path.append(os.path.dirname(os.path.realpath(source)))
        spec.loader.exec_module(source_module)
        func = getattr(source_module, target)
    except Exception as e:
        print('Something went wrong within the index, not the function!')
        raise e

    return func(request)

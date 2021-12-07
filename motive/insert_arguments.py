from typing import Callable
import inspect

from functools import partial


def insert_arguments(function, *sources) -> Callable:
    sig = inspect.signature(function)
    for p in sig.parameters.values():
        if p.kind is p.POSITIONAL_ONLY:
            raise TypeError("Cannot be used with positional only arguments")
    found_args = {}
    kwargs = set(sig.parameters.keys())

    for source in sources:
        for kw in tuple(kwargs):
            try:
                found_args[kw] = source[kw]
                kwargs.discard(kw)
                continue
            except (TypeError, KeyError):
                pass

    return partial(function, **found_args)

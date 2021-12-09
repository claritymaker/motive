import asyncio
import inspect
from asyncio import Event
from typing import Any, Dict, Iterable, Optional
from typing import Type

from motive.insert_arguments import insert_arguments
from motive.runner import IteratorError, RunnerError


def count(name, stop: Optional[int] = None, step: int = 1, start: int = 0):
    def _count(current_context: Dict[str, Any]):
        output = {}
        try:
            output[name] = current_context[name] + current_context[f"{name}_step"]
            if current_context[f"{name}_stop"] is not None:
                if (current_context[f"{name}_stop"] - output[name]) / current_context[
                    f"{name}_step"
                ] < 0:
                    raise IteratorError()

        except KeyError:
            output[f"{name}_step"] = step
            output[f"{name}_stop"] = stop
            output[name] = start
        return output

    _count.update_context = True
    return _count


def iterate(name, source: Iterable):
    def _iterate(current_context: Dict[str, Any]):
        output = {}
        try:
            output[f"{name}_finished"].append(output[name])
            try:
                output[name] = current_context[f"{name}_remaining"].pop(0)
            except IndexError:
                raise IteratorError()

        except KeyError:
            itr = (x for x in source)
            output[name] = next(itr)
            output[f"{name}_remaining"] = list(itr)
            output[f"{name}_finished"] = []

        return output

    _iterate.update_context = True
    return _iterate

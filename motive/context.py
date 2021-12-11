import asyncio
import inspect
from asyncio import Event
from typing import Any, Dict, Iterable, Optional
from typing import Type

from motive.insert_arguments import insert_arguments
from motive.properties import Properties


class Context:
    AUTO = object()

    def __init__(self):
        self._states: Dict[int, Dict[str, Any]] = {
            -1: {"running": Event(), "current_level": -1}
        }

    @property
    def current_level(self) -> int:
        return self._states[-1]["current_level"]

    @property
    def current_context(self) -> Dict[str, Any]:
        return self._states[self.current_level]

    def as_dict(self, level: Optional[int], start_level=0) -> Dict[str, Any]:
        if level is None:
            level = self.current_level

        itr = range(start_level, level + 1, 1 - 2 * int(start_level > level))
        output = {}
        for s in [self._states.get(x, {}) for x in itr]:
            output.update(s)

        return output

    def set(self, level: int, key: str, value):
        self._states.setdefault(level, {})[key] = value

    def update(self, level: int, source: Dict):
        for k, v in source.items():
            self.set(level, k, v)

    def __getitem__(self, item: str):
        for i in range(self.current_level, 0, -1):
            try:
                return self._states[i][item]
            except KeyError:
                pass
        raise KeyError(f"No item {item} currently in context")

    def __setitem__(self, key: str, value: Any):
        self.set(self.current_level, key, value)


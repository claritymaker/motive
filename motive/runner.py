import asyncio
from argument_inserter.insert_arguments import insert_arguments
from typing import Dict, Optional, Any, Iterable
from asyncio import Event
import inspect


class RunnerError(Exception):
    pass


class IteratorError(RunnerError):
    pass


class RunnerContext:
    def __init__(self):
        self._states: Dict[int, Dict[str, Any]] = {-1: {"running": Event(), "current_level": -1}}

    @property
    def current_level(self) -> int:
        return self._states[-1]["current_level"]

    @property
    def current_context(self) -> Dict[str, Any]:
        return self._states[self.current_level]

    def as_dict(self, level: Optional[int] = None, start_level=0) -> Dict[str, Any]:
        if level is None:
            level = self.current_level

        itr = range(start_level, level+1, 1-2*int(start_level>level))
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


def count(name, stop: Optional[int] = None, step: int = 1, start: int = 0):
    def _count(current_context: Dict[str, Any]):
        output = {}
        try:
            output[name] = current_context[name] + current_context[f"{name}_step"]
            if current_context[f"{name}_stop"] is not None:
                if (current_context[f"{name}_stop"] - output[name]) / current_context[f"{name}_step"] < 0:
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


async def run(callables, context: Optional[RunnerContext] = None, default_arguments=None, catch: Iterable[BaseException] = tuple(), force_sync=False):
    if context is None:
        context = RunnerContext()

    if default_arguments is None:
        default_arguments = []

    level = context._states[-1]["current_level"] + 1
    context._states[-1]["current_level"] = level
    context._states[level] = {}
    context._states[-1]["running"].set()

    try:
        current_await = []
        while True:
            for c in callables:
                await context._states[-1]["running"].wait()
                meta_arguments = {"context": context, "current_context": context.current_context}
                p = insert_arguments(c, *default_arguments, context.as_dict(), meta_arguments)
                if inspect.iscoroutinefunction(p):
                    current_await.append(p())
                    if not force_sync:
                        continue

                if current_await:
                    ans = asyncio.gather(current_await, return_exceptions=False)
                    for i, a in enumerate(ans):
                        try:
                            if current_await[i].update_context:
                                context.update(level, a)
                        except AttributeError:
                            pass
                    if force_sync:
                        continue

                try:
                    answer = p()
                    if c.update_context:
                        context.update(level, answer)
                except AttributeError:
                    pass
    except tuple(catch):
        pass
    finally:
        context._states[-1]["current_level"] = context.current_level - 1

    return context


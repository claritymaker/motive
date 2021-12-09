import asyncio
import inspect
from asyncio import Event
from typing import Any, Dict, Iterable, Optional
from typing import Type

from motive.insert_arguments import insert_arguments
from motive.runner_context import RunnerContext


class RunnerError(Exception):
    pass


class IteratorError(RunnerError):
    pass


async def run(
    callables,
    context: Optional[RunnerContext] = None,
    default_arguments=None,
    catch: Iterable[Type[BaseException]] = tuple(),
    force_sync=False,
):
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
        current_await_source = []
        while True:
            for c in callables:
                await context._states[-1]["running"].wait()
                meta_arguments = {
                    "context": context,
                    "current_context": context.current_context,
                }
                p = insert_arguments(
                    c, *default_arguments, context.as_dict(), meta_arguments
                )
                if inspect.iscoroutinefunction(p):
                    current_await.append(p())
                    current_await_source.append(p)
                    if not force_sync:
                        continue

                if current_await:
                    ans = await asyncio.gather(*current_await, return_exceptions=False)
                    # await ans
                    for i, a in enumerate(ans):
                        try:
                            if current_await_source[i].func.update_context:
                                context.update(level, a)
                        except AttributeError:
                            pass
                    current_await.clear()
                    current_await_source.clear()
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

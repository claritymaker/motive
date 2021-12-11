import asyncio
import inspect
from asyncio import Event
from typing import Any, Dict, Iterable, Optional
from typing import Type

from motive.insert_arguments import insert_arguments
from motive.properties import Properties
from motive.context import Context

async def run(
        callables,
        default_arguments=None,
        catch: Iterable[Type[BaseException]] = tuple(),
        context: Optional[Context] = None,
        force_sync=False,
):
    if context is None:
        context = Context()

    if default_arguments is None:
        default_arguments = []

    def no_op():
        # This is a sync function that we put at the end of a context level so that any dangling async functions get gathered
        pass

    level = context._states[-1]["current_level"] + 1
    context._states[-1]["current_level"] = level
    context._states[level] = {}
    context._states[-1]["running"].set()

    try:
        current_await = []
        current_await_props = []
        while True:
            for c in list(callables) + [no_op]:
                await context._states[-1]["running"].wait()

                current_props = getattr(c, "motive_properties", Properties())
                meta_arguments = {}
                if current_props.include_meta_arguments:
                    meta_arguments["context"] = context
                    meta_arguments["current_context"] = context.current_context
                    meta_arguments["default_arguments"] = default_arguments
                    meta_arguments["level"] = level

                p = insert_arguments(
                    c, *default_arguments, context.as_dict(level), meta_arguments
                )

                if inspect.iscoroutinefunction(p):
                    current_await.append(p())
                    current_await_props.append(current_props)
                    if not force_sync and not current_props.force_sync:
                        continue

                # we will only get here on a sync function
                if current_await:
                    ans = await asyncio.gather(*current_await, return_exceptions=False)
                    for i, a in enumerate(ans):
                        if current_await_props[i].update_context:
                            context.update(level, a)
                    current_await.clear()
                    current_await_props.clear()

                answer = p()
                if current_props.update_context:
                    context.update(level, answer)

    except tuple(catch):
        pass
    finally:
        context._states[-1]["current_level"] = context.current_level - 1

    return context

from typing import Iterable, Type

from motive.properties import Properties
from motive.run import run


def nest(
        callables,
        catch: Iterable[Type[BaseException]] = tuple(),
        force_sync=False,
):
    async def _nest(context):
        await run(callables=callables, catch=catch, force_sync=force_sync, context=context)

    _nest.motive_properties = Properties(force_sync=True, include_meta_arguments=True)

    return _nest

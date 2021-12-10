from typing import Iterable, Type

from motive.properties import Properties


def nest(
        self,
        callables,
        catch: Iterable[Type[BaseException]] = tuple(),
        force_sync=False,
):
    def _nest():
        await self.run(callables=callables, catch=catch, force_sync=force_sync)

    _nest.motive_properties = Properties(force_sync=True, include_meta_arguments=True)

    return _nest

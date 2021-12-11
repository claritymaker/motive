from typing import Any, Dict, Iterable, Optional, Union

from motive.exceptions import IteratorError
from motive.context import Properties
from motive.context import Context


def count(name: str, stop: Union[None, int, str] = None, step: Union[None, int, str] = 1, start: Union[int, str] = 0, inclusive: bool = False):
    def _count(level: int, context: Context, current_context: Dict[str, Any]):
        output = {}

        ctx_level = context.as_dict(level, start_level=level)

        # This will happen the first time this is executed in this context
        if name not in ctx_level:
            if isinstance(start, str):
                c_start = current_context[start]
            else:
                c_start = start
            output[name] = c_start

            # We don't want these to get looked now because we want them to get looked up each time it's run
            output[f"{name}_stop"] = stop
            output[f"{name}_step"] = step
            return output

        # We can now guarantee that the names are in the current_context
        c_val = current_context[name]
        c_step = current_context[f"{name}_step"]
        c_stop = current_context[f"{name}_stop"]
        if isinstance(c_stop, str):
            c_stop = current_context[c_stop]
        if isinstance(c_step, str):
            c_step = current_context[c_step]

        output[name] = c_val + c_step

        if c_stop is not None:
            if inclusive:
                if (c_stop - c_val) < c_step:
                    raise IteratorError()
            else:
                if (c_stop - c_val) <= c_step:
                    raise IteratorError()

        return output

    _count.motive_properties = Properties(update_context=True, include_meta_arguments=True)
    return _count


def iterate(name: str, source: Union[str, Iterable]):
    def _iterate(level: int, context: Context, current_context: Dict[str, Any]):
        output = {}
        ctx_level = context.as_dict(level, start_level=level)

        # This will happen the first time this is executed in this context
        if name not in ctx_level:
            if isinstance(source, str):
                output[f"{name}_remaining"] = list(current_context[source])
            else:
                output[f"{name}_remaining"] = list(source)

            output[name] = output[f"{name}_remaining"].pop(0)
            output[f"{name}_finished"] = []
            return output

        try:
            output[f"{name}_finished"] = current_context[f"{name}_finished"] + [current_context[name]]
            output[name] = current_context[f"{name}_remaining"].pop(0)
        except IndexError:
            raise IteratorError()

        return output

    _iterate.motive_properties = Properties(update_context=True, include_meta_arguments=True)
    return _iterate

from typing import Any, Dict, Iterable, Optional

from motive.runner import IteratorError


def count(name, stop: Optional[int] = None, step: int = 1, start: int = 0):
    def _count(current_context: Dict[str, Any]):
        output = {
            f"{name}_step": current_context.get(f"{name}_step", step),
            f"{name}_stop": current_context.get(f"{name}_stop", stop),
            name: current_context.get(name, start),
        }

        if name in current_context:
            output[name] = output[name] + output[f"{name}_step"]

        if output[f"{name}_stop"] is not None:
            if (output[f"{name}_stop"] - output[name]) / output[
                f"{name}_step"
            ] < 0:
                raise IteratorError()

        return output

    _count.update_context = True
    return _count


def iterate(name, source: Iterable):
    def _iterate(current_context: Dict[str, Any]):
        output = {
            f"{name}_finished": current_context.get(f"{name}_finished", []),
            f"{name}_remaining": current_context.get(f"{name}_remaining", list(source)),
        }
        if name in current_context:
            output[f"{name}_finished"].append(current_context[name])

        try:
            output[name] = output[f"{name}_remaining"].pop(0)
        except IndexError:
            raise IteratorError()

        return output

    _iterate.update_context = True
    return _iterate

from inspect import Signature, isclass
from enum import Enum

import json


def _default(e):
    if isclass(e) and issubclass(e, Enum):
        return {k: v.value for k, v in e.__members__.items()}

    if isinstance(e, Enum):
        return e.value

    if isclass(e):
        return e.__name__
    raise TypeError(f"got {e}")


def dump_signature(signature: Signature) -> str:
    sig = {}
    if signature.return_annotation is not Signature.empty:
        sig["return_annotation"] = signature.return_annotation

    parameters = {}
    for param in signature.parameters.values():
        p = {"kind": param.kind.name}
        if param.default is not Signature.empty:
            p["default"] = param.default
        if param.annotation is not Signature.empty:
            p["annotation"] = param.annotation
        parameters[param.name] = p

    sig["parameters"] = parameters
    return json.dumps(sig, default=_default)



from motive.dump_signature import dumps_callable
from enum import Enum


class ExampEnum(Enum):
    a = 1
    b = 2
    c = 3

def dumpable_func(a, b, *c, d=3):
    ...

def annotated_dumpable_func(a: int, b: float, *c: str, d: int = 3, e: ExampEnum = ExampEnum.b) -> int:
    return 1


def test_dump_signature():
    df = dumps_callable(dumpable_func)
    adf = dumps_callable(annotated_dumpable_func)

    exp_df = '{"parameters": {"a": {"kind": "POSITIONAL_OR_KEYWORD"}, "b": {"kind": "POSITIONAL_OR_KEYWORD"}, "c": {"kind": "VAR_POSITIONAL"}, "d": {"kind": "KEYWORD_ONLY", "default": 3}}}'
    exp_adf = '{"return_annotation": "int", "parameters": {"a": {"kind": "POSITIONAL_OR_KEYWORD", "annotation": "int"}, "b": {"kind": "POSITIONAL_OR_KEYWORD", "annotation": "float"}, "c": {"kind": "VAR_POSITIONAL", "annotation": "str"}, "d": {"kind": "KEYWORD_ONLY", "default": 3, "annotation": "int"}, "e": {"kind": "KEYWORD_ONLY", "default": 2, "annotation": {"a": 1, "b": 2, "c": 3}}}}'

    assert df == exp_df
    assert adf == exp_adf

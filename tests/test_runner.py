import asyncio
from asyncio import sleep

from motive.runner import IteratorError, run
from motive.runner_context import RunnerContext
from motive.itr import count, iterate


def _get_current_level(context):
    return context[-1]["current_level"]


def test_runner_sync():
    def t1(test):
        return {f"t1_{test}": test ** 2}

    def t2(test):
        return {f"t2_{test}": test ** 2}

    def t3(test):
        return {f"t3_{test}": test ** 2}

    t1.update_context = True
    t2.update_context = False

    default_arguments = {"a": 1, "b": 2}
    callables = [count("test", 5), t1]
    co = run(callables, default_arguments=default_arguments, catch=(IteratorError,))
    ctx = asyncio.run(co)
    assert ctx.as_dict(1) == {
        "test_step": 1,
        "test_stop": 5,
        "test": 5,
        "t1_0": 0,
        "t1_1": 1,
        "t1_2": 4,
        "t1_3": 9,
        "t1_4": 16,
        "t1_5": 25,
    }


def test_runner_async():
    async def t1(test):
        await sleep(test)
        print(f"t1_{test}")
        return {f"t1_{test}": test ** 2}

    async def t2(test):
        await sleep(test)
        return {f"t2_{test}": test ** 2}

    async def t3(test):
        await sleep(test)
        return {f"t3_{test}": test ** 2}

    t1.update_context = True
    t2.update_context = False

    default_arguments = {"a": 1, "b": 2}
    callables = [count("test", 5), t1, t2]
    co = run(callables, default_arguments=default_arguments, catch=(IteratorError,))
    ctx = asyncio.run(co)
    assert ctx.as_dict(1) == {
        "test_step": 1,
        "test_stop": 5,
        "test": 5,
        "t1_0": 0,
        "t1_1": 1,
        "t1_2": 4,
        "t1_3": 9,
        "t1_4": 16,
        "t1_5": 25,
    }
    return ctx


if __name__ == "__main__":
    test_runner_async()

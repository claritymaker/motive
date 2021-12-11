import asyncio
from asyncio import sleep
from datetime import datetime

from motive.run import run
from motive.properties import Properties
from motive.exceptions import IteratorError
from motive.nest import nest
from motive.itr import count


def test_runner_sync():
    def t1(test):
        return {f"t1_{test}": test ** 2}

    def t2(test):
        return {f"t2_{test}": test ** 2}

    def t3(test):
        return {f"t3_{test}": test ** 2}

    t1.motive_properties = Properties(update_context = True)
    t2.motive_properties = Properties(update_context = False)

    default_arguments = {"a": 1, "b": 2}
    callables = [count("test", 5), t1, t2, t3]
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
        await sleep(.1)
        return {f"t1_{test}": test ** 2}

    async def t2(test):
        await sleep(.1)
        return {f"t2_{test}": test ** 2}

    async def t3(test):
        await sleep(.1)
        return {f"t3_{test}": test ** 2}

    t1.motive_properties = Properties(update_context = True)
    t2.motive_properties = Properties(update_context = False)

    default_arguments = {"a": 1, "b": 2}
    callables = [count("test", 5), t1, t2, t3]
    co = run(callables, default_arguments=default_arguments, catch=(IteratorError,))
    start_time = datetime.now()
    ctx = asyncio.run(co)
    end_time = datetime.now()
    assert 0.4 < (end_time-start_time).total_seconds() < 1
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


def test_runner_nested():
    def t1(test):
        return {f"t1_{test}": test ** 2}

    def t2(test, test2):
        return {f"t2_{test},{test2}": test * test2}

    t1.motive_properties = Properties(update_context = True)
    t2.motive_properties = Properties(update_context = True)

    default_arguments = {"a": 1, "b": 2}
    callables = [
        count("test", 5),
        t1,
        nest([count("test2", 5), t2], catch=(IteratorError, )),
    ]
    co = run(callables, default_arguments=default_arguments, catch=(IteratorError,))
    ctx = asyncio.run(co)
    assert ctx.as_dict(0) == {
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
        "test2_step": 1,
        "test2_stop": 5,
        "test2": 5,
        "t2_5,0": 0,
        "t2_5,1": 5,
        "t2_5,2": 10,
        "t2_5,3": 15,
        "t2_5,4": 20,
        "t2_5,5": 25,
    }



if __name__ == "__main__":
    test_runner_async()

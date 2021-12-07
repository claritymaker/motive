from argument_inserter.runner import RunnerContext, run, count, IteratorError, iterate
import asyncio


def _get_current_level(context):
    return context[-1]["current_level"]


def test_iterate():
    source = [1,2,3,4]
    ctx = {}
    itr = iterate("test", source)
    for i in range(len(source) + 1):
        try:
            ans = itr(ctx)
            ctx.update(ans)
            assert ctx == {"test": source[i], "test_finished": source[0:i-1], "test_remaining": source[i:]}
        except IteratorError:
            if i == len(source):
                return None
            else:
                raise
    else:
        raise IteratorError()


def test_count():
    ctx = {}
    c = count("test", 10)
    for i in range(11):
        try:
            ans = c(ctx)
            ctx.update(ans)
            assert ctx == {"test": i, "test_step": 1, "test_stop": 10}
        except IteratorError:
            if i > 10:
                pass
            else:
                raise


def test_runner_sync():
    def t1(test):
        return {f"t1_{test}": test ** 2}
    t1.update_context = True


    default_arguments = {"a": 1, "b": 2}
    callables = [count("test", 5), t1]
    co = run(callables, default_arguments=default_arguments, catch=(IteratorError, ))
    ctx = asyncio.run(co)

    return ctx


if __name__ == "__main__":
    test_runner_sync()

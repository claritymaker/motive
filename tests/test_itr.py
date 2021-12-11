from motive.exceptions import IteratorError
from motive.itr import count, iterate
from motive.context import Context


def test_iterate():
    source = [1, 2, 3, 4]
    ctx = Context()
    itr = iterate("test", source)
    for i in range(len(source) + 1):
        try:
            ans = itr(level=0, context=ctx, current_context=ctx.as_dict(0))
            ctx.update(0, ans)
            expected_ans = {
                "test": source[i],
                "test_finished": source[0:i],
                "test_remaining": source[i + 1 :],
            }
            assert ctx.as_dict(0) == expected_ans
        except IteratorError:
            if i == len(source):
                return None
            else:
                raise
    else:
        raise IteratorError()


def test_count():
    ctx = Context()
    c = count("test", 10)
    for i in range(11):
        try:
            ans = c(context=ctx, current_context=ctx.as_dict(0), level=0)
            ctx.update(0, ans)
            assert ctx.as_dict(0) == {"test": i, "test_step": 1, "test_stop": 10}
        except IteratorError:
            if i > 10:
                pass
            else:
                raise

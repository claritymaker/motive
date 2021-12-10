from motive.exceptions import IteratorError
from motive.itr import count, iterate


def test_iterate():
    source = [1, 2, 3, 4]
    ctx = {}
    itr = iterate("test", source)
    for i in range(len(source) + 1):
        try:
            ans = itr(ctx)
            ctx.update(ans)
            expected_ans = {
                "test": source[i],
                "test_finished": source[0:i],
                "test_remaining": source[i + 1 :],
            }
            assert ctx == expected_ans
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

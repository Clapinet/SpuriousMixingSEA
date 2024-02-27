import time


def time_fun(fun):
    def timed_fun(*args, **kwargs):
        t0 = time.time()
        res = fun(*args, **kwargs)
        print(f"Function {fun.__name__!r} executed in {(time.time() - t0):.4f}s")
        return res

    return timed_fun


def check_matching(value, dic, name, additional_condition=True):
    """
        Check that given value is in dic and does verify another condition and
    raise explicit error if not verified.
    """
    if value not in dic and additional_condition:
        raise KeyError(
            f"Unknown {name} <{value}>. "
            f"Please provide one of the following : ",
            tuple(dic.keys()),
        )

import functools
import itertools
import operator

import numpy as np
import perfplot


def forfor(a):
    return [item for sublist in a for item in sublist]


def sum_brackets(a):
    return sum(a, [])


def functools_reduce(a):
    return functools.reduce(operator.concat, a)


def functools_reduce_iconcat(a):
    return functools.reduce(operator.iconcat, a, [])


def itertools_chain(a):
    return list(itertools.chain.from_iterable(a))


def numpy_flat(a):
    return list(np.array(a).flat)


def numpy_concatenate(a):
    return list(np.concatenate(a))


def extend(a):
    out = []
    for sublist in a:
        out.extend(sublist)
    return out


b = perfplot.bench(
    setup=lambda n: [list(range(10))] * n,
    # setup=lambda n: [list(range(n))] * 10,
    kernels=[
        forfor,
        sum_brackets,
        functools_reduce,
        functools_reduce_iconcat,
        itertools_chain,
        numpy_flat,
        numpy_concatenate,
        extend,
    ],
    n_range=[2 ** k for k in range(16)],
    xlabel="num lists (of length 10)",
    # xlabel="len lists (10 lists total)"
)
b.save("out.png")
b.show()
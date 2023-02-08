from time import perf_counter
from functools import wraps
from contextlib import asynccontextmanager, contextmanager
from collections import defaultdict

GROUPS = defaultdict(list)

def func(group):
    """Annotate normal function"""

    def dec(f):
        def wrapper(*args, **kwargs):

            GROUPS[group].append({
                "id":id(f), 
                "name": f.__name__, 
                "args": args,
                "kwargs": kwargs,
                "delta": None,
            })

            print(f"Annotating {group}")
            print(f"{args}, {kwargs}")

            before = perf_counter()

            r = f(*args, **kwargs)

            after = perf_counter()
            delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"

            for gfunc in GROUPS[group]:
                if gfunc['id'] == id(f):
                    gfunc["delta"] = delta

            # print(delta)
            return r

        return wrapper

    return dec

def async_func(group):
    """Annotate async function"""

    def dec(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            GROUPS[group].append({
                "id":id(f), 
                "name": f.__name__, 
                "args": args,
                "kwargs": kwargs,
                "delta": None,
            })

            print(f"Annotating {group}")
            print(f"{args}, {kwargs}")
            before = perf_counter()
            r = await f(*args, **kwargs)
            after = perf_counter()
            delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"

            for gfunc in GROUPS[group]:
                if gfunc['id'] == id(f):
                    gfunc["delta"] = delta

            # print(delta)
            return r

        return wrapper

    return dec

@contextmanager
def block(group):
    print(f"Annotating Block {group}")
    before = perf_counter()
    yield
    after = perf_counter()
    delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"
    # print(delta)

@asynccontextmanager
async def async_block(group):
    print(f"Annotating Block {group}")
    before = perf_counter()
    yield
    after = perf_counter()
    delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"
    # print(delta)


def async_bugme(groups):
    def dec(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            r = await f(*args, **kwargs)
            for group in groups:
                for gfunc in GROUPS[group]:
                    print(f"{gfunc['name']}({gfunc['args']},{gfunc['kwargs']}) {gfunc['delta']}")
            return r
        return wrapper
    return dec

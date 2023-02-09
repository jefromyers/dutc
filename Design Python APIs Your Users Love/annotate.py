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

            before = perf_counter()

            r = f(*args, **kwargs)

            after = perf_counter()
            delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"

            for gfunc in GROUPS[group]:
                if gfunc['id'] == id(f):
                    gfunc["delta"] = delta

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

            before = perf_counter()
            r = await f(*args, **kwargs)
            after = perf_counter()
            delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"

            for gfunc in GROUPS[group]:
                if gfunc['id'] == id(f):
                    gfunc["delta"] = delta

            return r

        return wrapper

    return dec

@contextmanager
def block(group, name):
    GROUPS[group].append({
        "id": name,
        "name": "Block", 
        "delta": None,
    })
    before = perf_counter()
    yield
    after = perf_counter()
    delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"
    for gfunc in GROUPS[group]:
        if gfunc['id'] == name:
            gfunc["delta"] = delta

@asynccontextmanager
async def async_block(group, name):
    GROUPS[group].append({
        "id": name,
        "name": "Block", 
        "delta": None,
    })
    before = perf_counter()
    yield
    after = perf_counter()
    delta = f"\N{mathematical bold capital delta}t: {after - before:.4f}s"
    for gfunc in GROUPS[group]:
        if gfunc['id'] == name:
            gfunc["delta"] = delta


def async_bugme(groups):
    def dec(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            r = await f(*args, **kwargs)
            for group in groups:
                print("")
                print(f"--- {group} ---")
                for gfunc in GROUPS[group]:
                    if gfunc['name'] == "Block":
                        print(f"{gfunc['id']} {gfunc['delta']}")
                    else:
                        print(f"{gfunc['name']}({gfunc['args']},{gfunc['kwargs']}) {gfunc['delta']}")
            return r
        return wrapper
    return dec

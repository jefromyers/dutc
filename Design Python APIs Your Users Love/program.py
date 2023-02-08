from time import sleep
from asyncio import run
import annotate

@annotate.func(group="Group A")
def f(a):
    sleep(.2)
    return "func"


@annotate.async_func("Group B")
async def af(a):
    return "async func"

@annotate.async_bugme(groups=["Group A", "Group B", "Group D"])
async def go():

    f("hi")
    f("dee")
    f("hoo")
    await af("hi")

    with annotate.block(group="Group C"):
        for _ in range(10_000):
            ...

    async with annotate.async_block(group="Group D"):
        for _ in range(10_000):
            ...

    # print(annotate.GROUPS)    

if __name__ == "__main__":
    run(go())

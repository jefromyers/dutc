from time import sleep
from asyncio import run

import annotate


@annotate.async_func(group="Report")
async def fetch():
    print("Acquiring data")
    return "data"

@annotate.func(group="Report")
def process(data):
    print("Cleaning data")
    return "clean data"

@annotate.async_func(group="Report")
async def make_report(data):
    print("Creating data")
    return "awesome report"

@annotate.async_bugme(groups=["Report"])
async def go():
    """ Mock """

    data = await fetch() 
    data = process(data)
    report = await make_report(data)

    with annotate.block(group="Report", name="Delivery"):
        print("Delivering report")

if __name__ == "__main__":
    run(go())

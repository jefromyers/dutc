from random import choice, seed
from datetime import date
from string import ascii_lowercase

from notifications import notify

seed(0)


@notify("Must use new datasouce by", by=date(2023, 3, 1))
def acquire():
    print(f"Acquiring data")
    data = [choice([*ascii_lowercase]) for _ in range(10)]
    return data


@notify("Date format is dd-mm-yyyy")
def process(data):
    print(f"Processing {data}")
    return [*reversed(data)]


@notify("Hack! double check analysis algorithm")
def analize(data):
    print(f"Analyzing {data}")
    data = {i: a for i, a in enumerate(data)}
    return data


if __name__ == "__main__":
    print(f"Do stuff")
    data = acquire()
    processed_data = process(data)
    report = analize(processed_data)
    print(report)

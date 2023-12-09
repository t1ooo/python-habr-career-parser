import csv
import dataclasses
from typing import TextIO
from habr_career_parser.rss_parser import Item


def to_csv(path_or_io: str | TextIO, items: list[Item]):
    with open(path_or_io, "w", newline="") if isinstance(
        path_or_io, str
    ) else path_or_io as csvfile:
        writer = csv.writer(csvfile)
        fields = sorted([field.name for field in dataclasses.fields(Item)])
        writer.writerow(fields)
        for item in items:
            print(item)
            item_dict = dataclasses.asdict(item)
            row = [item_dict[k] for k in fields]
            print(row)
            writer.writerow(row)

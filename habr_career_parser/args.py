from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)
from functools import partial
import enum
import os
from typing import Type, TypeVar
from habr_career_parser.rss_parser import (
    Employment,
    Skill,
    Sort,
    delay_from_float,
    page_from_int,
)


def _page_arg(value: str):
    try:
        v = int(value)
    except ValueError:
        raise ArgumentTypeError("must be an int")
    try:
        return page_from_int(v)
    except ValueError as e:
        raise ArgumentTypeError(e)


def _delay_arg(value: str):
    try:
        v = float(value)
    except ValueError:
        raise ArgumentTypeError("must be a float")
    try:
        return delay_from_float(v)
    except ValueError as e:
        raise ArgumentTypeError(e)


_T = TypeVar("_T", bound=Type[enum.Enum])


def _enum_arg(e: _T, value: str) -> _T:
    try:
        value = value.upper()
        return e[value]
    except KeyError:
        raise ArgumentTypeError(f"must be a one of {e}")


def _add_enum(
    ap: ArgumentParser, name_or_flags: str, e: Type[enum.Enum], help: str = ""
):
    ap.add_argument(
        name_or_flags,
        type=partial(_enum_arg, e),
        choices=list(e),
        default=str(next(iter(e))),
        help=help,
    )


def _save_arg(value: str):
    try:
        dir = os.path.dirname(value)
        if dir != "":
            os.makedirs(dir, exist_ok=True)
        open(value, "w")
        return value
    except OSError as e:
        raise ArgumentTypeError(e.strerror)


def parse_args(args: list[str]) -> Namespace:
    ap = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    _add_enum(ap, "--sort", Sort, help="sort result")
    ap.add_argument(
        "--remote", action="store_true", default=False, help="parse by remove jobs"
    )
    _add_enum(ap, "--skill", Skill, help="parse by skill")
    _add_enum(ap, "--employment", Employment, help="parse by employment")
    ap.add_argument("--query", type=str, default="", help="parse by search query")
    ap.add_argument(
        "--delay",
        type=_delay_arg,
        default=delay_from_float(3.0),
        help="delay between requests",
    )
    ap.add_argument(
        "--page",
        type=_page_arg,
        help="page number for parsing or all results, if omitted",
    )
    ap.add_argument(
        "--save", type=_save_arg, help="path to save the CSV file or standard output, if omitted"
    )

    return ap.parse_args(args)

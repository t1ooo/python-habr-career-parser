import pytest
from habr_career_parser.args import parse_args


def _call_parse_args(capsys, args: list[str]) -> str:  # type: ignore
    try:
        parse_args(args)
    except SystemExit:
        pass
    return capsys.readouterr().err


args_data = dict(
    sort=["none", "date", "salary_desc", "salary_asc"],
    skill=["none", "intern", "junior", "middle", "senior", "lead"],
    employment=["none", "full_time", "part_time"],
    query=["", "test"],
    delay=["0", "2", "3"],
    page=["1", "2", "3"],
    save=["data.txt"],
)


@pytest.mark.parametrize(
    "name_val", [(k, v) for k, vs in args_data.items() for v in vs]
)
def test_parse_args(capsys, name_val: tuple[str, str]):  # type: ignore
    name, val = name_val
    print(name, val)
    args = ["--" + name, val]
    assert _call_parse_args(capsys, args) == "", (name, val)


bool_args_data = ["remote"]


@pytest.mark.parametrize("name", bool_args_data)
def test_parse_args_bool_arg(capsys, name: str):  # type: ignore
    print(name)
    args = ["--" + name]
    assert _call_parse_args(capsys, args) == "", name

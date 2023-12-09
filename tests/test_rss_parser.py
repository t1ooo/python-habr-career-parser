from pytest_httpx import HTTPXMock
from habr_career_parser.rss_parser import *


def _item(i: int):
    s = str(i)
    return Item(
        title="title" + s,
        description="description" + s,
        author="author" + s,
        pub_date="pubDate" + s,
        link="link" + s,
        guid="guid" + s,
        image="image" + s,
    )


def test_parse(httpx_mock: HTTPXMock):
    parser = RssParser()

    content = open("tests/test_data/rss.xml", "rb").read()
    httpx_mock.add_response(content=content)
    assert parser.parse(page_from_int(1)) == [_item(1), _item(2)]

    content = open("tests/test_data/rss_empty.xml", "rb").read()
    httpx_mock.add_response(content=content)
    assert parser.parse(page_from_int(1)) == []


def test_build_url():
    parser = RssParser()
    page = Page(1)
    result = parser._build_url(page)  # type: ignore
    assert (
        result == "https://career.habr.com/vacancies/rss?currency=RUR&page=1&type=all"
    )

    parser = RssParser(
        sort=Sort.DATE,
        remote=True,
        skill=Skill.MIDDLE,
        employment=Employment.PART_TIME,
        query="test",
    )
    page = Page(1)
    result = parser._build_url(page)  # type: ignore
    assert (
        result
        == "https://career.habr.com/vacancies/rss?currency=RUR&employment_type=part_time&page=1&q=test&qid=middle&remote=1&sort=date&type=all"
    )

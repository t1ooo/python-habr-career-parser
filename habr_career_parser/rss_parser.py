import dataclasses
import enum
import logging
import time
from typing import NewType
from fake_useragent import UserAgent
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import urlencode


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclasses.dataclass(frozen=True)
class Item:
    title: str | None
    description: str | None
    author: str | None
    pub_date: str | None
    link: str | None
    guid: str | None
    image: str | None


def get_xml_element_text(item: ET.Element, tag: str):
    e = item.find(tag)
    if e is None:
        return None
    return e.text


class Sort(str, enum.Enum):
    NONE = ""
    DATE = "date"
    SALARY_DESC = "salary_desc"
    SALARY_ASC = "salary_asc"

    def __str__(self) -> str:
        return self.name.lower()


class Skill(str, enum.Enum):
    NONE = ""
    INTERN = "1"
    JUNIOR = "3"
    MIDDLE = "4"
    SENIOR = "5"
    LEAD = "6"

    def __str__(self) -> str:
        return self.name.lower()


class Employment(str, enum.Enum):
    NONE = ""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"

    def __str__(self) -> str:
        return self.name.lower()


Page = NewType("Page", int)


def page_from_int(v: int) -> Page:
    if not (v >= 1):
        raise ValueError("must be >= 1")
    return Page(v)


Delay = NewType("Page", float)


def delay_from_float(v: float) -> Delay:
    if not (v >= 0):
        raise ValueError("must be >= 0")
    return Delay(v)


class RssParser:
    def __init__(
        self,
        sort: Sort = Sort.NONE,
        remote: bool = False,
        skill: Skill = Skill.NONE,
        employment: Employment = Employment.NONE,
        query: str = "",
        delay: Delay = Delay(3.0),
    ):
        self.sort = sort
        self.remote = remote
        self.skill = skill
        self.employment = employment
        self.query = query
        self.delay = delay

        self.ua = UserAgent(min_percentage=1.0)

    def _request(self, url: str) -> httpx.Response:
        resp = httpx.get(
            url,
            headers={
                "User-Agent": self.ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
        )
        return resp

    def _parse_rss(self, xml: str) -> list[Item]:
        tree = ET.ElementTree(ET.fromstring(xml))

        root = tree.getroot()

        items: list[Item] = []
        for item in root.iter("item"):
            item = Item(
                title=get_xml_element_text(item, "title"),
                description=get_xml_element_text(item, "description"),
                author=get_xml_element_text(item, "author"),
                pub_date=get_xml_element_text(item, "pubDate"),
                link=get_xml_element_text(item, "link"),
                guid=get_xml_element_text(item, "guid"),
                image=get_xml_element_text(item, "image"),
            )

            empty_keys = [k for k, v in dataclasses.asdict(item).items() if v is None]
            if empty_keys:
                logger.warning(f"Item {empty_keys} is None")

            items.append(item)

        return items

    def _build_url(
        self,
        page: Page,
    ) -> str:
        base_url = "https://career.habr.com/vacancies/rss"
        base_params = dict(currency="RUR", type="all")

        params = dict(
            sort=self.sort,
            remote=self.remote,
            qid=self.skill,
            employment_type=self.employment,
            page=page,
            q=self.query,
        )
        params.update(base_params)

        prepared_params = {}
        for k, v in sorted(params.items(), key=lambda x: x[0]):
            if v in [None, "", False, 0]:
                pass
            elif isinstance(v, bool):
                prepared_params[k] = int(v)  # convert bool to int
            else:
                prepared_params[k] = v

        query = urlencode(prepared_params)
        return base_url + "?" + query

    def _parse_url(self, url: str) -> list[Item]:
        for _ in range(3):
            resp = self._request(url)
            try:
                items = self._parse_rss(resp.content.decode())
                return items
            except (ET.ParseError, httpx.HTTPError) as e:
                logger.warning(f"{url}: {e}")
                time.sleep(self.delay)

        logger.info(f"{url}: fail to parse")
        return []

    def _parse_page(self, page: Page) -> list[Item]:
        url = self._build_url(page)
        logger.info(f"{url}: parse")
        items = self._parse_url(url)
        return items

    def _parse_all(self) -> list[Item]:
        page = Page(1)

        items = []
        while True:
            try:
                page_items = self._parse_page(page)
                if len(page_items) == 0:
                    break
                items.append(page_items)
                time.sleep(self.delay)
                page = page_from_int(page + 1)
            except KeyboardInterrupt:
                break
        return items

    def parse(self, page: Page | None = None) -> list[Item]:
        if page is None:
            return self._parse_all()
        else:
            return self._parse_page(page)

import re
import requests

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

from core.models import Tag


class AbstractParser(ABC):
    def __init__(self, tags: list[Tag]) -> None:
        self._tags = tags

    def match_tags(self, url: str) -> list[Tag]:
        text = self._parse_vacancy(url)
        tags = self._intext_match(text)

        return tags

    @abstractmethod
    def _parse_vacancy(self, url: str) -> str:
        pass

    def _intext_match(self, text: str) -> list[Tag]:
        word2tag = {word.strip(): t for t in self._tags for word in t.intext_match.split(";") + [t.keyword]}
        matched_words = list(filter(lambda x: x in text, word2tag.keys()))
        tags = list(set(word2tag[word] for word in matched_words))
        return tags


class HHParser(AbstractParser):
    def _parse_vacancy(self, url: str) -> str:
        response = requests.get(url)
        soup = BeautifulSoup(response.content)

        vacancy_title = soup.find("div", {"class": "vacancy-title"}).text or ""
        vacancy_section = soup.find("div", {"class": "vacancy-section"}).text or ""
        resume_section = soup.find("div", {"class": "resume-wrapper"}).text or ""

        return " ".join([vacancy_title, vacancy_section, resume_section])


class UniversalParser(AbstractParser):
    def _parse_vacancy(self, url: str) -> str:
        response = requests.get(url)
        return response.content.decode("utf-8")


PARSERS_COLLECTION = [
    (r".*\.hh\.ru/*", HHParser),
    (r".*", UniversalParser),
]


def parse_url_tags(url: str, tags: list[Tag]) -> list[Tag]:
    parser = None

    for parser_regex, parser in PARSERS_COLLECTION:
        if re.match(parser_regex, url):
            break

    tags = parser(tags).match_tags(url)

    return tags

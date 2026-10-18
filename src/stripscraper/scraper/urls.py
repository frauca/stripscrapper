"""Competition scraper to get all classifications."""

from typing import List, Set, Tuple
from loguru import logger

from stripscraper.models import Classification
from stripscraper.parser import HttpxParser, PlaywrightParser


class FixedUrlsScraper:

    def __init__(self, urls: List[str]):
        self.parser = PlaywrightParser()
        self.urls = urls

    def scrape_all_categories(self) -> List[Classification]:
        logger.info("Scraping all category")

        results = []

        for url in self.urls:

            classification = self.parser.parse_classification(url)

            results.append(classification)

        return results

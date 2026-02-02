"""Volleyball parser with dataclasses."""

from typing import List
from loguru import logger
import httpx
import gzip

from stripscraper.models import TeamStats, Group, Classification
from stripscraper.parser.html import HtmlParser


class HttpxParser:

    def __init__(self):
        logger.info("Initializing ClassificationParser")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ca,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def parse_classification(self, url: str) -> Classification:
        logger.info("Downloading " + url)

        response = httpx.get(url, headers=self.headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        html = response.text

        logger.success("Page downloaded (" + str(len(html)) + " bytes)")

        parser = HtmlParser()
        return parser.parse_classification(html)
from loguru import logger
from playwright.sync_api import sync_playwright

from stripscraper.models import Classification
from stripscraper.parser.html import HtmlParser


class PlaywrightParser:

    def parse_classification(self, url: str) -> Classification:
        html = self._download_with_playwright(url)

        parser = HtmlParser()
        return parser.parse_classification(html)



    def _download_with_playwright(self, url: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            logger.info(f"Loading {url} with Playwright...")
            page.goto(url, wait_until='networkidle')

            html = page.content()
            browser.close()

            logger.success(f"Page rendered ({len(html)} bytes)")
            return html
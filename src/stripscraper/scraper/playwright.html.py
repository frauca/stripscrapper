from typing import List

from loguru import logger
from playwright.sync_api import sync_playwright

from stripscraper.models import Classification
from stripscraper.parser import PlaywrightParser


class PlaywrightScraper:

    def __init__(self):
        self.parser = PlaywrightParser()
        self.base_url = "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1746&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria={category_id}&id_competicion={competition_id}"

    def scrape_all_categories(self) -> List[Classification]:
        logger.info("Scraping all category")

        results = []

        for url in self.urls:

            classification = self.parser.parse_classification(url)

            results.append(classification)

        return results

    def _scrape_all_categories(self) -> List[str]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1746&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=171&id_competicion=549"

            logger.info(f"Loading {url} with Playwright...")
            page.goto(url, wait_until='networkidle')

            page.locator("#select2-categorias-container").click()
            page.wait_for_timeout(500)

            options_elements = page.locator("#categorias option")

            options_data = []
            for i in range(options_elements.count()):
                option = options_elements.nth(i)

                text = option.inner_text().strip()
                value = option.get_attribute("value")

                options_data.append({
                    "text": text,
                    "value": value
                })
            return [opt['value'] for opt in options_data]

if __name__ == "__main__":
    scraper = PlaywrightScraper()
    categories = scraper._scrape_all_categories()
    for cat in categories:
        logger.info(cat)

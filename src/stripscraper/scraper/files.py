from pathlib import Path
from typing import List

from loguru import logger

from stripscraper.models import Classification
from stripscraper.parser.html import HtmlParser
from charset_normalizer import from_path

class FilesUrlsScraper:

    def __init__(self):
        self.parser = HtmlParser()
        self.files = ["./outputs/Cadet4a.html",
                     "./outputs/Juvenil4a.html"]

    def read_file_safely(self, path:Path)->str:
        results = from_path(path)
        best_guess = results.best()

        logger.info(f"Codificació detectada: {best_guess.encoding}")
        return path.read_text(encoding=best_guess.encoding, errors='replace')


    def scrape_all_categories(self) -> List[Classification]:
        logger.info("Scraping all category")

        results = []

        for file in self.files:
            html = Path(file).read_text(encoding="utf-8", errors='replace')
            classification = self.parser.parse_classification(html)

            results.append(classification)

        return results

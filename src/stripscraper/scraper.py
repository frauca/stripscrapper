"""Competition scraper to get all classifications."""

from typing import List, Set, Tuple
from loguru import logger

from stripscraper.models import Classification
from stripscraper.parser import ClassificationParser


class CompetitionScraper:

    def __init__(self):
        self.parser = ClassificationParser()
        self.urls = ["https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1746&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=171&id_competicion=549",
                     "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1750&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=176&id_competicion=566",
                     "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1975&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=173&id_competicion=551",
                     "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1977&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=178&id_competicion=568"]

    def scrape_all_categories(self) -> List[Classification]:
        logger.info("Scraping all category")

        results = []

        for url in self.urls:

            classification = self.parser.parse_classification(url)

            results.append(classification)

        return results

from pathlib import Path

from loguru import logger

from stripscraper.classifier import Classifier
from stripscraper.exporters.csv import CSVExporter
from stripscraper.models import GlobalClassification
from stripscraper.scraper import CompetitionScraper
from stripscraper.strip import StripCalculator


def main():
    logger.info("Iniciant web scraper per a fcvolei.cat")

    scraper = CompetitionScraper()
    classifications = scraper.scrape_all_categories()

    strip = StripCalculator()
    classifications = strip.calculate_strip_classifications(classifications)

    classifier = Classifier()
    classifications = classifier.classify(classifications)

    export_dir = Path("outputs")

    to_csv = CSVExporter()
    to_csv.export(classifications, export_dir)



if __name__ == "__main__":
    main()

from pathlib import Path

from loguru import logger

from stripscraper.classifier import Classifier
from stripscraper.exporters.csv import CSVExporter
from stripscraper.exporters.excel import ExcelExporter
from stripscraper.exporters.pdf import PDFExporter
from stripscraper.scraper import FixedUrlsScraper as CompetitionScraper
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

    to_xls = ExcelExporter()
    to_xls.export(classifications, export_dir)

    to_pdf = PDFExporter()
    to_pdf.export(classifications, export_dir)



if __name__ == "__main__":
    main()

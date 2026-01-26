
from loguru import logger
from stripscraper.scraper import CompetitionScraper


def main():
    logger.info("Iniciant web scraper per a fcvolei.cat")

    scraper = CompetitionScraper()
    classifications = scraper.scrape_all_categories()

    for classification in classifications:
        logger.info(f"\n=== {classification.competition} - {classification.category} ===")
        for group in classification.groups:
            logger.info(f"\n{group.name}:")
            top3 = group.get_top(3)
            for i, team in enumerate(top3, 1):
                logger.info(f"  {i}. {team.name}")
                logger.info(f"     PT: {team.total_points} | "
                      f"{team.matches_won}W-{team.matches_lost}L | "
                      f"Sets: {team.sets_for}-{team.sets_against} ({team.sets_difference:+d})  | "
                      f"Points: {team.points_for}-{team.points_against} ({team.points_difference:+d})")


if __name__ == "__main__":
    main()

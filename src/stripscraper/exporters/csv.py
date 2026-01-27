"""CSV Exporter - Exporta classificacions a CSV."""

import csv
from datetime import datetime
from typing import List
from pathlib import Path

from loguru import logger

from stripscraper.models import GlobalClassification


class CSVExporter:

    def export(self, classifications: List[GlobalClassification], filepath: Path):
        for classification in classifications:
            self._export_classification(classification, filepath)

    def _export_classification(self, classification: GlobalClassification, filepath: Path):
        file_name = f"{classification.category}-{datetime.today().strftime('%Y-%m-%d')}.csv"
        csv_file = Path(filepath / file_name)
        csv_file.unlink(missing_ok=True)
        csv_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting {csv_file}")

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            writer.writerow([
                'Posició Global',
                'Equip',
                '% Punts',
                'Punts',
                'Grup',
                'Posició Grup',
                'Partits',
                'Victòries',
                'Derrotes',
                'Sets Favor',
                'Sets Contra',
                'Dif Sets',
                'Punts Favor',
                'Punts Contra',
                'Dif Punts'
            ])

            for i, team in enumerate(classification.teams, start=1):
                writer.writerow([
                    i,
                    team.stats.name,
                    team.stats.points_percentage,
                    team.stats.total_points,
                    team.group,
                    team.stats.position,
                    team.stats.matches_played,
                    team.stats.matches_won,
                    team.stats.matches_lost,
                    team.stats.sets_for,
                    team.stats.sets_against,
                    team.stats.sets_difference,
                    team.stats.points_for,
                    team.stats.points_against,
                    team.stats.points_difference
                ])

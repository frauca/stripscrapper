"""Classifier - Junta i ordena equips de totes les classificacions."""

from typing import List

from stripscraper.models import Classification, GlobalClassification, TeamWithContext


class Classifier:

    def classify(self, classifications: List[Classification]) -> List[GlobalClassification]:
        global_class = []

        for classification in classifications:
            global_class.append(self._global_classify(classification))

        return global_class

    def _global_classify(self, classification: Classification) ->GlobalClassification:
        teams = []

        for group in classification.groups:
            for team in group.teams:
                team_with_context = TeamWithContext(
                    stats=team,
                    competition=classification.competition,
                    category=classification.category,
                    group=group.name
                )
                teams.append(team_with_context)

        teams.sort(
            key=lambda t: (
                -t.stats.points_percentage,
                -t.stats.matches_won,
                -t.stats.sets_difference,
                -t.stats.points_difference
            )
        )

        return GlobalClassification(
            url=classification.url,
            competition=classification.competition,
            category=classification.category,
            teams=teams
        )
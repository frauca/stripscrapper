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
                t.stats.position,
                -t.stats.points_percentage,
                -t.stats.matches_won,
                -t.stats.sets_difference,
                -t.stats.points_difference
            )
        )

        self._snake_distribute(teams, 4)

        return GlobalClassification(
            competition=classification.competition,
            category=classification.category,
            teams=teams
        )

    def _snake_distribute(self, teams: List[TeamWithContext], num_groups: int) -> None:
        for i, team in enumerate(teams):
            cycle_pos = i % (num_groups * 2)
            if cycle_pos < num_groups:
                team.stats.new_group = cycle_pos + 1
            else:
                team.stats.new_group = num_groups * 2 - cycle_pos
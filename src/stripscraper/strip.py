"""Strip calculator - Combina classificacions de Cadet i Juvenil."""

from typing import List, Dict, Tuple
from loguru import logger

from stripscraper.models import TeamStats, Group, Classification


class StripCalculator:

    def __init__(self):
        logger.info("Initializing StripCalculator")

    def calculate_strip_classifications(self, classifications: List[Classification]) -> List[Classification]:
        logger.info("Calculant classificacions de tira...")

        divisions = self._group_by_division(classifications)

        strip_classifications = []

        for division, (cadet_class, juvenil_class) in divisions.items():
            logger.info(f"Processant divisió: {division}")
            strip_class = self._combine_classifications(cadet_class, juvenil_class, division)
            strip_classifications.append(strip_class)

        logger.success(f"Calculades {len(strip_classifications)} classificacions de tira")
        return strip_classifications

    def _group_by_division(self, classifications: List[Classification]) -> Dict[str, Tuple[Classification, Classification]]:
        cadet_by_div = {}
        juvenil_by_div = {}

        for classification in classifications:
            division = self._extract_division(classification.category)

            if "Cadet" in classification.category:
                cadet_by_div[division] = classification
            elif "Juvenil" in classification.category:
                juvenil_by_div[division] = classification

        divisions = {}
        for division in cadet_by_div.keys():
            if division not in juvenil_by_div:
                raise ValueError(f"No s'ha trobat Juvenil per la divisió {division}")
            divisions[division] = (cadet_by_div[division], juvenil_by_div[division])
            logger.info(f"Emparellada divisió {division}: Cadet + Juvenil")

        return divisions

    def _extract_division(self, category: str) -> str:
        if "2a Div" in category:
            return "2a Div"
        elif "4a Div" in category:
            return "4a Div"
        elif "3a Div" in category:
            return "3a Div"
        elif "1a Div" in category:
            return "1a Div"
        else:
            raise ValueError(f"Divisió desconeguda a la categoria: {category}")

    def _combine_classifications(self, cadet: Classification, juvenil: Classification, division: str) -> Classification:
        strip_classification = Classification(
            url="",
            competition=f"Tira {division}",
            category=f"Tira {division} Fem",
            groups=[]
        )

        cadet_groups_dict = {g.name: g for g in cadet.groups}
        juvenil_groups_dict = {g.name: g for g in juvenil.groups}

        if len(cadet_groups_dict) != len(juvenil_groups_dict):
            raise ValueError(f"Numero de grups diferent: Cadet={len(cadet_groups_dict)}, Juvenil={len(juvenil_groups_dict)}")

        for group_name in sorted(cadet_groups_dict.keys()):
            cadet_group = cadet_groups_dict[group_name]
            juvenil_group = juvenil_groups_dict[group_name]

            strip_group = self._combine_groups(cadet_group, juvenil_group, group_name)
            strip_classification.groups.append(strip_group)

        return strip_classification

    def _combine_groups(self, cadet_group: Group, juvenil_group: Group, group_name: str) -> Group:
        cadet_teams = {team.name: team for team in cadet_group.teams}
        juvenil_teams = {team.name: team for team in juvenil_group.teams}

        common_teams = set(cadet_teams.keys()) & set(juvenil_teams.keys())

        if len(common_teams) == 0:
            raise ValueError(f"Cap equip comú trobat al grup {group_name}")

        logger.info(f"Grup {group_name}: {len(common_teams)} equips amb Cadet+Juvenil")

        strip_teams = []
        for team_name in common_teams:
            cadet_team = cadet_teams[team_name]
            juvenil_team = juvenil_teams[team_name]

            strip_team = self._combine_teams(cadet_group,cadet_team, juvenil_team)
            strip_teams.append(strip_team)

        strip_teams.sort(key=lambda t: (
                -t.points_percentage,
                -t.matches_won,
                -t.sets_difference,
                -t.points_difference
            ))

        for i, team in enumerate(strip_teams, start=1):
            team.position = i

        strip_group = Group(
            name=group_name,
            round=max(cadet_group.round, juvenil_group.round),
            teams=strip_teams
        )

        return strip_group

    def _combine_teams(self, group: Group, cadet: TeamStats, juvenil: TeamStats) -> TeamStats:
        total_points = cadet.total_points + juvenil.total_points
        matches_played = cadet.matches_played + juvenil.matches_played
        matches_won = cadet.matches_won + juvenil.matches_won
        matches_lost = cadet.matches_lost + juvenil.matches_lost
        sets_for = cadet.sets_for + juvenil.sets_for
        sets_against = cadet.sets_against + juvenil.sets_against
        points_for = cadet.points_for + juvenil.points_for
        points_against = cadet.points_against + juvenil.points_against

        points_percentage = self._current_percentage(total_points, len(group.teams)*4-4)
        win_percentage = (matches_won / matches_played) * 100 if matches_played > 0 else 0
        loss_percentage = (matches_lost / matches_played) * 100 if matches_played > 0 else 0
        avg_points_for = points_for / matches_played if matches_played > 0 else 0
        avg_points_against = points_against / matches_played if matches_played > 0 else 0

        recent_form = cadet.recent_form + juvenil.recent_form

        return TeamStats(
            position=0,
            name=cadet.name,
            url=cadet.url,
            recent_form=recent_form,
            total_points=total_points,
            points_percentage=points_percentage,
            matches_played=matches_played,
            matches_won=matches_won,
            win_percentage=win_percentage,
            matches_lost=matches_lost,
            loss_percentage=loss_percentage,
            sets_for=sets_for,
            sets_against=sets_against,
            points_for=points_for,
            avg_points_for=avg_points_for,
            points_against=points_against,
            avg_points_against=avg_points_against,
            victories_3_sets=cadet.victories_3_sets + juvenil.victories_3_sets,
            victories_2_sets=cadet.victories_2_sets + juvenil.victories_2_sets,
            defeats_1_point=cadet.defeats_1_point + juvenil.defeats_1_point,
            defeats_0_points=cadet.defeats_0_points + juvenil.defeats_0_points,
        )

    def _current_percentage(self, total_points: int, matches_played: int) -> float:
        return total_points / (matches_played * 3) * 100 if matches_played > 0 else 0
"""Strip calculator - Combina classificacions de Cadet i Juvenil."""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from loguru import logger

from stripscraper.models import TeamStats, Group, Classification


@dataclass
class TeamMatch:
    nom_definitiu: str
    nom_cadet: str
    nom_juvenil: str
    cadet_team: TeamStats
    juvenil_team: TeamStats


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
        matches = self._match_teams(cadet_group.teams, juvenil_group.teams, group_name)

        logger.info(f"Grup {group_name}: {len(matches)} equips amb Cadet+Juvenil")

        strip_teams = []
        for match in matches:
            strip_team = self._combine_teams(cadet_group, match.cadet_team, match.juvenil_team)
            strip_team.name = match.nom_definitiu
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

    def _match_teams(self, cadet_teams: List[TeamStats], juvenil_teams: List[TeamStats], group_name: str) -> List[TeamMatch]:
        if len(cadet_teams) != len(juvenil_teams):
            raise ValueError(f"Grup {group_name}: diferent nombre d'equips (Cadet={len(cadet_teams)}, Juvenil={len(juvenil_teams)})")

        cadet_normalized = [(i, team, self._normalize_name(team.name)) for i, team in enumerate(cadet_teams)]
        juvenil_normalized = [(i, team, self._normalize_name(team.name)) for i, team in enumerate(juvenil_teams)]

        matches = []
        used_juvenil_idx = set()

        for cadet_idx, cadet_team, cadet_norm in cadet_normalized:
            for juvenil_idx, juvenil_team, juvenil_norm in juvenil_normalized:
                if juvenil_idx in used_juvenil_idx:
                    continue

                if cadet_norm == juvenil_norm:
                    nom_definitiu = self._get_definitive_name(cadet_team.name, juvenil_team.name)
                    matches.append(TeamMatch(
                        nom_definitiu=nom_definitiu,
                        nom_cadet=cadet_team.name,
                        nom_juvenil=juvenil_team.name,
                        cadet_team=cadet_team,
                        juvenil_team=juvenil_team
                    ))
                    used_juvenil_idx.add(juvenil_idx)
                    logger.debug(f"  Match exacte: '{cadet_team.name}' ↔ '{juvenil_team.name}' → '{nom_definitiu}'")
                    break

        unmatched_cadet = [(idx, team) for idx, team, _ in cadet_normalized if not any(m.cadet_team == team for m in matches)]
        unmatched_juvenil = [(idx, team) for idx, team, _ in juvenil_normalized if idx not in used_juvenil_idx]

        if unmatched_cadet or unmatched_juvenil:
            logger.warning(f"Grup {group_name}: {len(unmatched_cadet)} equips sense match exacte, intentant matching fuzzy...")
            fuzzy_matches = self._fuzzy_match(unmatched_cadet, unmatched_juvenil, group_name)
            matches.extend(fuzzy_matches)

        if len(matches) != len(cadet_teams):
            unmatched_cadet_names = [team.name for idx, team, _ in cadet_normalized if not any(m.cadet_team == team for m in matches)]
            unmatched_juvenil_names = [team.name for idx, team, _ in juvenil_normalized if not any(m.juvenil_team == team for m in matches)]
            logger.error(f"Grup {group_name} - Equips sense parella:")
            logger.error(f"  Cadet: {unmatched_cadet_names}")
            logger.error(f"  Juvenil: {unmatched_juvenil_names}")
            raise ValueError(f"No s'han pogut emparellar tots els equips del grup {group_name}")

        return matches

    def _fuzzy_match(self, cadet_teams: List[Tuple[int, TeamStats]], juvenil_teams: List[Tuple[int, TeamStats]], group_name: str) -> List[TeamMatch]:
        matches = []
        used_juvenil_idx = set()

        for cadet_idx, cadet_team in cadet_teams:
            best_match = None
            best_match_idx = None
            best_score = 0

            cadet_norm = self._normalize_name(cadet_team.name)
            cadet_words = set(cadet_norm.split())

            for juvenil_idx, juvenil_team in juvenil_teams:
                if juvenil_idx in used_juvenil_idx:
                    continue

                juvenil_norm = self._normalize_name(juvenil_team.name)
                juvenil_words = set(juvenil_norm.split())

                common_words = cadet_words & juvenil_words

                if not common_words:
                    continue

                min_words = min(len(cadet_words), len(juvenil_words))
                max_words = max(len(cadet_words), len(juvenil_words))

                word_score = len(common_words) / min_words

                char_score = self._character_similarity(cadet_norm, juvenil_norm)

                score = word_score * 0.8 + char_score * 0.2

                if score > best_score:
                    best_score = score
                    best_match = juvenil_team
                    best_match_idx = juvenil_idx

            if best_match and best_score > 0.3:
                nom_definitiu = self._get_definitive_name(cadet_team.name, best_match.name)
                matches.append(TeamMatch(
                    nom_definitiu=nom_definitiu,
                    nom_cadet=cadet_team.name,
                    nom_juvenil=best_match.name,
                    cadet_team=cadet_team,
                    juvenil_team=best_match
                ))
                used_juvenil_idx.add(best_match_idx)
                logger.info(f"  Match fuzzy ({best_score:.2f}): '{cadet_team.name}' ↔ '{best_match.name}' → '{nom_definitiu}'")

        return matches

    def _character_similarity(self, s1: str, s2: str) -> float:
        if not s1 or not s2:
            return 0.0

        longer = s1 if len(s1) >= len(s2) else s2
        shorter = s2 if len(s1) >= len(s2) else s1

        if len(longer) == 0:
            return 1.0

        matches = sum(1 for i, c in enumerate(shorter) if i < len(longer) and c == longer[i])
        return matches / len(longer)

    def _normalize_name(self, name: str) -> str:
        import unicodedata

        normalized = name.upper()
        normalized = unicodedata.normalize('NFKD', normalized)
        normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])

        normalized = ''.join([c if c.isalnum() or c.isspace() else ' ' for c in normalized])

        words = normalized.split()
        words = [w for w in words if w not in ['CADET', 'JUVENIL', 'JFG', 'CFG']]

        return ' '.join(words).strip()

    def _get_definitive_name(self, cadet_name: str, juvenil_name: str) -> str:
        longer_name = cadet_name if len(cadet_name) >= len(juvenil_name) else juvenil_name

        definitive = longer_name
        for word in ['CADET', 'JUVENIL', 'Cadet', 'Juvenil', 'cadet', 'juvenil']:
            definitive = definitive.replace(word, '')

        definitive = ' '.join(definitive.split())

        return definitive.strip()

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

    def _normalized_to_7(self, total_points: int, matches_played: int) -> float:
        if matches_played == 0:
            return 0
        projected_points = (total_points / matches_played) * 7
        return (projected_points / 21) * 100

    def _normalized_with_penalty(self, total_points: int, matches_played: int) -> float:
        if matches_played == 0:
            return 0
        projected_points = (total_points / matches_played) * 7
        confidence = matches_played / 7
        adjusted_points = projected_points * (0.7 + 0.3 * confidence)
        return (adjusted_points / 21) * 100

    def _weighted_difficulty(self, total_points: int, matches_played: int) -> float:
        if matches_played == 0:
            return 0
        difficulty_multiplier = 1.0 + (matches_played - 6) * 0.05
        weighted_points = total_points * difficulty_multiplier
        normalized_points = (weighted_points / matches_played) * 7
        return (normalized_points / 21) * 100

    def _rounding_to_8(self, total_points: int, group_teams: int) -> float:
        if group_teams == 8:
            return total_points
        if group_teams == 7:
            return (total_points / 7) * 8
        raise ValueError(f"Tenim un grup amb {group_teams} equips!")
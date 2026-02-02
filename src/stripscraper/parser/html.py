from bs4 import BeautifulSoup
from typing import List
from loguru import logger

from stripscraper import formula
from stripscraper.models import Classification, Group, TeamStats


class HtmlParser:
    def parse_classification(self, html: str) -> Classification:

        soup = BeautifulSoup(html, 'lxml')

        competition = self._extract_competition(soup)
        category = self._extract_category(soup)
        groups = self._extract_groups(soup)

        logger.success("Parsing completed: " + str(len(groups)) + " groups")

        return Classification(
            competition=competition,
            category=category,
            groups=groups
        )

    def _extract_competition(self, soup: BeautifulSoup) -> str:
        h2 = soup.find('h2')
        if not h2:
            raise ValueError("No s'ha trobat l'element h2 amb la competició")

        text = h2.get_text(strip=True)
        if 'CLASIFICACIONES' in text:
            return text.replace('CLASIFICACIONES', '').strip()

        return text

    def _extract_category(self, soup: BeautifulSoup) -> str:
        h2 = soup.find('h2')
        if not h2:
            raise ValueError("No s'ha trobat l'element h2 amb la categoria")

        text = h2.get_text(strip=True)
        if 'CLASIFICACIONES' in text:
            return text.replace('CLASIFICACIONES', '').strip()

        return text

    def _extract_groups(self, soup: BeautifulSoup) -> List[Group]:
        groups = []

        all_h4 = soup.find_all('h4')
        logger.info(f"Trobats {len(all_h4)} elements h4")

        for i, h4 in enumerate(all_h4):
            text = h4.get_text(strip=True)
            if i < 20:  # Log primers 20
                logger.debug(f"H4 #{i}: {text}")

            if 'PRIMERA FASE - GRUP' in text:
                logger.info(f"Trobat grup: {text}")
                group = self._parse_group(h4)
                groups.append(group)

        return groups

    def _parse_group(self, h4_element) -> Group:
        group_name = h4_element.get_text(strip=True).replace("PRIMERA FASE - ","")

        round_h4 = h4_element.find_next('h4')
        round_num = 0
        if round_h4 and 'Jornada:' in round_h4.get_text():
            round_num = int(round_h4.get_text(strip=True).replace('Jornada:', '').strip())

        table = h4_element.find_next('table')
        if not table:
            raise ValueError(f"No s'ha trobat taula per al grup {group_name}")

        teams = self._parse_table(table)

        if len(teams) == 0:
            raise ValueError(f"No s'han trobat equips per al grup {group_name}")

        return Group(name=group_name, round=round_num, teams=teams)

    def _parse_table(self, table) -> List[TeamStats]:
        teams = []
        rows = table.find_all('tr')[1:]

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 14:
                continue

            team = self._parse_team_row(cols)
            teams.append(team)

        return teams

    def _parse_team_row(self, cols) -> TeamStats:
        if len(cols) < 15:
            raise ValueError(f"Fila amb menys de 14 columnes: {len(cols)}")

        team_link = cols[1].find('a')
        team_name = team_link.get_text(strip=True) if team_link else cols[1].get_text(strip=True)


        form = cols[2].get_text(strip=True)

        def safe_int(text: str) -> int:
            cleaned = text.strip().replace('%', '')
            parts = cleaned.split()
            if not parts:
                raise ValueError(f"No s'ha pogut parsejar enter de: {text}")
            return int(parts[0])

        def safe_float(text: str) -> float:
            cleaned = text.strip().replace('ptos./part.', '').replace('sets/part.', '')
            parts = cleaned.split()
            if len(parts) >= 2:
                return float(parts[-2])
            if parts:
                return float(parts[0])
            raise ValueError(f"No s'ha pogut parsejar float de: {text}")

        total_points = safe_int(cols[3].get_text())
        matches_played = safe_int(cols[4].get_text())

        matches_won_parts = cols[5].get_text().split()
        if not matches_won_parts:
            raise ValueError(f"No s'ha pogut parsejar victòries de: {cols[5].get_text()}")

        matches_lost_parts = cols[6].get_text().split()
        if not matches_lost_parts:
            raise ValueError(f"No s'ha pogut parsejar derrotes de: {cols[6].get_text()}")

        points_percentage = formula.current_percentage(total_points, matches_played * 3)

        return TeamStats(
            position=safe_int(cols[0].get_text()),
            name=team_name,
            recent_form=form,
            total_points=total_points,
            points_percentage=points_percentage,
            matches_played=matches_played,
            matches_won=safe_int(matches_won_parts[0]),
            win_percentage=safe_int(matches_won_parts[1]) if len(matches_won_parts) > 1 else 0,
            matches_lost=safe_int(matches_lost_parts[0]),
            loss_percentage=safe_int(matches_lost_parts[1]) if len(matches_lost_parts) > 1 else 0,
            sets_for=safe_int(cols[7].get_text()),
            sets_against=safe_int(cols[8].get_text()),
            points_for=safe_int(cols[9].get_text()),
            avg_points_for=safe_float(cols[9].get_text()),
            points_against=safe_int(cols[10].get_text()),
            avg_points_against=safe_float(cols[10].get_text()),
            victories_3_sets=safe_int(cols[11].get_text()),
            victories_2_sets=safe_int(cols[12].get_text()),
            defeats_1_point=safe_int(cols[13].get_text()),
            defeats_0_points=safe_int(cols[14].get_text()) if len(cols) > 14 else 0,
        )
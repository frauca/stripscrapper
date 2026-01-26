"""Volleyball parser with dataclasses."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
import httpx


@dataclass
class TeamStats:
    position: int
    name: str
    url: str
    recent_form: str
    total_points: int
    matches_played: int
    matches_won: int
    win_percentage: int
    matches_lost: int
    loss_percentage: int
    sets_for: int
    sets_against: int
    points_for: int
    avg_points_for: float
    points_against: int
    avg_points_against: float
    victories_3_sets: int
    victories_2_sets: int
    defeats_1_point: int
    defeats_0_points: int

    @property
    def sets_difference(self) -> int:
        return self.sets_for - self.sets_against

    @property
    def points_difference(self) -> int:
        return self.points_for - self.points_against

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Group:
    name: str
    round: int
    teams: List[TeamStats] = field(default_factory=list)

    @property
    def total_teams(self) -> int:
        return len(self.teams)

    @property
    def leader(self) -> Optional[TeamStats]:
        return self.teams[0] if self.teams else None

    def get_top(self, n: int = 3) -> List[TeamStats]:
        return self.teams[:n]

    def find_team(self, name: str) -> Optional[TeamStats]:
        name_upper = name.upper()
        for team in self.teams:
            if name_upper in team.name.upper():
                return team
        return None

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'round': self.round,
            'total_teams': self.total_teams,
            'teams': [t.to_dict() for t in self.teams]
        }


@dataclass
class Classification:
    url: str
    competition: str
    category: str
    groups: List[Group] = field(default_factory=list)

    @property
    def total_groups(self) -> int:
        return len(self.groups)

    @property
    def total_teams(self) -> int:
        return sum(g.total_teams for g in self.groups)

    def get_group(self, name: str) -> Optional[Group]:
        for group in self.groups:
            if name.upper() in group.name.upper():
                return group
        return None

    def find_team_global(self, name: str) -> List[tuple[Group, TeamStats]]:
        results = []
        for group in self.groups:
            team = group.find_team(name)
            if team:
                results.append((group, team))
        return results

    def to_dict(self) -> dict:
        return {
            'url': self.url,
            'competition': self.competition,
            'category': self.category,
            'total_groups': self.total_groups,
            'total_teams': self.total_teams,
            'groups': [g.to_dict() for g in self.groups]
        }


class ClassificationParser:

    def __init__(self):
        logger.info("Initializing ClassificationParser")

    def parse_classification(self, url: str) -> Classification:
        logger.info("Downloading " + url)

        response = httpx.get(url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        html = response.text

        logger.success("Page downloaded (" + str(len(html)) + " bytes)")

        soup = BeautifulSoup(html, 'lxml')

        competition = self._extract_competition(soup)
        category = self._extract_category(soup)
        groups = self._extract_groups(soup, url)

        logger.success("Parsing completed: " + str(len(groups)) + " groups")

        return Classification(
            url=url,
            competition=competition,
            category=category,
            groups=groups
        )

    def _extract_competition(self, soup: BeautifulSoup) -> str:
        h2 = soup.find('h2')
        if h2:
            text = h2.get_text(strip=True)
            if 'CLASIFICACIONES' in text:
                return text.replace('CLASIFICACIONES', '').strip()
        return 'Unknown'

    def _extract_category(self, soup: BeautifulSoup) -> str:
        h2 = soup.find('h2')
        if h2:
            parts = h2.get_text(strip=True).split()
            if len(parts) >= 3:
                return ' '.join(parts[-4:])
        return 'Unknown'

    def _extract_groups(self, soup: BeautifulSoup, base_url: str) -> List[Group]:
        groups = []
        h4_groups = soup.find_all('h4')

        for h4 in h4_groups:
            text = h4.get_text(strip=True)
            if 'PRIMERA FASE - GRUP' in text:
                group = self._parse_group(h4, base_url)
                if group:
                    groups.append(group)

        return groups

    def _parse_group(self, h4_element, base_url: str) -> Optional[Group]:
        group_name = h4_element.get_text(strip=True)

        round_h4 = h4_element.find_next_sibling('h4')
        round_num = 0
        if round_h4 and 'Jornada:' in round_h4.get_text():
            round_num = int(round_h4.get_text(strip=True).replace('Jornada:', '').strip())

        table = h4_element.find_next('table')
        if not table:
            return None

        teams = self._parse_table(table, base_url)

        return Group(name=group_name, round=round_num, teams=teams)

    def _parse_table(self, table, base_url: str) -> List[TeamStats]:
        teams = []
        rows = table.find_all('tr')[1:]

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 14:
                continue

            team = self._parse_team_row(cols, base_url)
            if team:
                teams.append(team)

        return teams

    def _parse_team_row(self, cols, base_url: str) -> Optional[TeamStats]:
        team_link = cols[1].find('a')
        team_name = team_link.get_text(strip=True) if team_link else cols[1].get_text(strip=True)

        team_url = ''
        if team_link and team_link.get('href'):
            href = team_link.get('href')
            if not href.startswith('http'):
                base = base_url.split('clasificacion_completa.php')[0]
                team_url = base + href
            else:
                team_url = href

        form = cols[2].get_text(strip=True)

        def safe_int(text: str) -> int:
            cleaned = text.strip().replace('%', '')
            parts = cleaned.split()
            if parts:
                return int(parts[0])
            return 0

        def safe_float(text: str) -> float:
            cleaned = text.strip().replace('ptos./part.', '').replace('sets/part.', '')
            parts = cleaned.split()
            if len(parts) >= 2:
                return float(parts[-2])
            if parts:
                return float(parts[0])
            return 0.0

        return TeamStats(
            position=safe_int(cols[0].get_text()),
            name=team_name,
            url=team_url,
            recent_form=form,
            total_points=safe_int(cols[3].get_text()),
            matches_played=safe_int(cols[4].get_text()),
            matches_won=safe_int(cols[5].get_text().split()[0]),
            win_percentage=safe_int(cols[5].get_text().split()[-1]),
            matches_lost=safe_int(cols[6].get_text().split()[0]),
            loss_percentage=safe_int(cols[6].get_text().split()[-1]),
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

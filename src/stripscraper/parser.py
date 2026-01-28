"""Volleyball parser with dataclasses."""

from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
import httpx

from stripscraper.models import TeamStats, Group, Classification


class ClassificationParser:

    def __init__(self):
        logger.info("Initializing ClassificationParser")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ca,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def parse_classification(self, url: str) -> Classification:
        logger.info("Downloading " + url)

        response = httpx.get(url, headers=self.headers, timeout=30.0, follow_redirects=True)
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
        total_points = safe_int(cols[3].get_text())
        matches_played = safe_int(cols[4].get_text())
        return TeamStats(
            position=safe_int(cols[0].get_text()),
            name=team_name,
            url=team_url,
            recent_form=form,
            total_points=total_points,
            points_percentage =  total_points/ (matches_played * 3) * 100 if matches_played > 0 else 0,
            matches_played=matches_played,
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

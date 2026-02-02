from dataclasses import dataclass, asdict, field
from typing import List, Optional


@dataclass
class TeamStats:
    position: int
    name: str
    recent_form: str
    total_points: int
    points_percentage: float
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


@dataclass
class TeamWithContext:
    stats: TeamStats
    competition: str
    category: str
    group: str


@dataclass
class GlobalClassification:
    competition: str
    category: str
    teams: List[TeamWithContext] = field(default_factory=list)
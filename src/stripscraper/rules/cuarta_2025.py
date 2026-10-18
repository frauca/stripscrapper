# ===== src/stripscraper/rules/cuarta_2025.py =====
from stripscraper.models import Classification, GlobalClassification, TeamStats, TeamWithContext
from stripscraper.rules.base import Edition


class Cuarta2025(Edition):
    name = "2025_cuarta"
    division = "4a Div"
    urls = ["https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1746&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=171&id_competicion=549",
                     "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1750&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=176&id_competicion=566",
                     "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1975&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=173&id_competicion=551",
                     "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=1977&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=178&id_competicion=568"]
    num_groups = 4

    def ranking_key(self, team: TeamStats) -> tuple:
        return (
            -team.points_percentage,
            -team.matches_won,
            -team.sets_difference,
            -team.points_difference,
        )

    def distribute_one(self, strip: Classification) -> GlobalClassification:
        teams = [
            TeamWithContext(stats=team, competition=strip.competition, category=strip.category, group=group.name)
            for group in strip.groups
            for team in group.teams
        ]
        teams.sort(key=lambda t: (t.stats.position,) + self.ranking_key(t.stats))

        for i, team in enumerate(teams):
            cycle = i % (self.num_groups * 2)
            if cycle < self.num_groups:
                team.phase_two = str(cycle + 1)
            else:
                team.phase_two = str(self.num_groups * 2 - cycle)

        return GlobalClassification(competition=strip.competition, category=strip.category, teams=teams)

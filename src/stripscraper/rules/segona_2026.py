# ===== src/stripscraper/rules/segona_2026.py =====
from stripscraper.models import Classification, GlobalClassification, TeamStats, TeamWithContext
from stripscraper.rules.base import Edition, ratio


class Segona2026(Edition):
    name = "2026_segona"
    division = "2a Div"
    urls = ["https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=3688&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=357&id_competicion=1387",
            "https://resultadosvoleibol.isquad.es/clasificacion_completa.php?seleccion=0&id=3689&id_ambito=0&id_territorial=17&id_superficie=1&iframe=0&id_categoria=361&id_competicion=1393"]
    block_size = 4
    blocks = (("Promoció", 0), ("Permanència", 4))

    def ranking_key(self, team: TeamStats) -> tuple:
        return (
            -team.total_points,
            -team.matches_won,
            -ratio(team.sets_for, team.sets_against),
            -ratio(team.points_for, team.points_against),
        )

    def distribute_one(self, strip: Classification) -> GlobalClassification:
        groups = sorted(strip.groups, key=lambda g: g.name)
        contexts = [
            [
                TeamWithContext(stats=team, competition=strip.competition, category=strip.category, group=group.name)
                for team in group.teams
            ]
            for group in groups
        ]

        teams = []
        for label, offset in self.blocks:
            slices = [c[offset:offset + self.block_size] for c in contexts]
            g1, g2, g3, g4 = sorted(slices, key=lambda s: self.ranking_key(s[0].stats))

            extrem_pair, central_pair = (g1, g4), (g2, g3)
            (e1, e2), (c1, c2) = extrem_pair, central_pair

            assignments = {
                "1": [e1[0], e1[3], e2[0], e2[3], c1[1], c1[2], c2[1], c2[2]],
                "2": [c1[0], c1[3], c2[0], c2[3], e1[1], e1[2], e2[1], e2[2]],
            }

            for letter, members in assignments.items():
                for team in members:
                    team.phase_two = label + " " + letter
                    teams.append(team)
            teams.sort(key=lambda t: self.ranking_key(t.stats))

        return GlobalClassification(competition=strip.competition, category=strip.category, teams=teams)
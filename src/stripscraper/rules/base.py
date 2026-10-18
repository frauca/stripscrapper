
# ===== src/stripscraper/rules/base.py =====
from abc import ABC, abstractmethod
from typing import List

from stripscraper.models import Classification, GlobalClassification, TeamStats


class Edition(ABC):
    name: str
    division: str
    urls: List[str]

    @abstractmethod
    def ranking_key(self, team: TeamStats) -> tuple:
        ...

    @abstractmethod
    def distribute_one(self, strip: Classification) -> GlobalClassification:
        ...

    def distribute(self, classifications: List[Classification]) -> List[GlobalClassification]:
        return [self.distribute_one(c) for c in classifications]

def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else float("inf")

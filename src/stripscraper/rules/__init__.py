# ===== src/stripscraper/rules/__init__.py =====
from stripscraper.rules.cuarta_2025 import Cuarta2025
from stripscraper.rules.segona_2026 import Segona2026

EDITIONS = {edition.name: edition for edition in (Cuarta2025(), Segona2026())}
def current_percentage(total_points: int, matches_played: int) -> float:
    return total_points / (matches_played * 3) * 100 if matches_played > 0 else 0


def normalized_to_7(total_points: int, matches_played: int) -> float:
    if matches_played == 0:
        return 0
    projected_points = (total_points / matches_played) * 7
    return (projected_points / 21) * 100


def normalized_with_penalty(total_points: int, matches_played: int) -> float:
    if matches_played == 0:
        return 0
    projected_points = (total_points / matches_played) * 7
    confidence = matches_played / 7
    adjusted_points = projected_points * (0.7 + 0.3 * confidence)
    return (adjusted_points / 21) * 100


def weighted_difficulty(total_points: int, matches_played: int) -> float:
    if matches_played == 0:
        return 0
    difficulty_multiplier = 1.0 + (matches_played - 6) * 0.05
    weighted_points = total_points * difficulty_multiplier
    normalized_points = (weighted_points / matches_played) * 7
    return (normalized_points / 21) * 100


def rounding_to_8(total_points: int, group_teams: int) -> float:
    if group_teams == 8:
        return total_points
    if group_teams == 7:
        return (total_points / 7) * 8
    raise ValueError(f"Tenim un grup amb {group_teams} equips!")
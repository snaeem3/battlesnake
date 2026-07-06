# Must sum to 100
WEIGHTS = {
    "ffScore": 60,
    "foodDirection": 40,
    # "enemyDistance": 0,
}

def scoreMove(move, boardArea:int) -> int:
    MAX_FF_SCORE = boardArea
    if not move["isSafe"]:
        return 0

    score = 0

    score += (move["ffScore"] / MAX_FF_SCORE) * WEIGHTS["ffScore"]
    score += (1 if move["foodDirection"] else 0) * WEIGHTS["foodDirection"]
    # score += move["enemyDistance"] * WEIGHTS["enemyDistance"]

    return round(score)
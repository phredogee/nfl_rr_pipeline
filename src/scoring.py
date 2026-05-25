# src/scoring.py
# Scoring engine — calculates fantasy points from raw stats using league scoring config
# Supports all configurable scoring categories from the League Manager

def calculate_points(stats: dict, scoring: dict) -> float:
    """
    Calculate fantasy points for a single player's weekly stats.

    Args:
        stats:   dict of raw stats from weekly_stats table
        scoring: league scoring_config dict from leagues.json

    Returns:
        float: total fantasy points for the week
    """
    total = 0.0

    def val(key: str) -> float:
        """Safely get a stat value, defaulting to 0."""
        return float(stats.get(key) or 0)

    def cfg(category: str, key: str) -> float:
        """Safely get a scoring config value, defaulting to 0."""
        return float(scoring.get(category, {}).get(key) or 0)

    # ── Passing ────────────────────────────────────────────────────────────────
    pass_yds = val("passing_yards")
    pass_tds = val("passing_tds")
    ints     = val("interceptions")
    sack_yds = val("sack_yards")
    sack_fum = val("sack_fumbles_lost")
    comps    = val("completions")
    incomps  = val("attempts") - val("completions")
    pass_2pt = val("passing_2pt_conversions")

    ypp = cfg("passing", "yards_per_point")
    if ypp > 0:
        total += pass_yds / ypp
    total += pass_tds  * cfg("passing", "td_points")
    total += ints      * cfg("passing", "int_deduction")        # negative
    total += sack_yds  * cfg("passing", "sack_yard_deduction")  # negative
    total += sack_fum  * cfg("passing", "sack_fumble_lost")     # negative
    total += comps     * cfg("passing", "completion_bonus")
    total += incomps   * cfg("passing", "incomplete_deduction") # negative
    total += pass_2pt  * cfg("passing", "two_pt_conversion")
    if pass_yds >= 300:
        total += cfg("passing", "bonus_300_yards")
    if pass_yds >= 400:
        total += cfg("passing", "bonus_400_yards")

    # ── Rushing ────────────────────────────────────────────────────────────────
    rush_yds = val("rushing_yards")
    rush_tds = val("rushing_tds")
    rush_fum = val("rushing_fumbles_lost")
    rush_2pt = val("rushing_2pt_conversions")

    ypp = cfg("rushing", "yards_per_point")
    if ypp > 0:
        total += rush_yds / ypp
    total += rush_tds * cfg("rushing", "td_points")
    total += rush_fum * cfg("rushing", "fumble_lost_deduction")  # negative
    total += rush_2pt * cfg("rushing", "two_pt_conversion")
    if rush_yds >= 100:
        total += cfg("rushing", "bonus_100_yards")
    if rush_yds >= 200:
        total += cfg("rushing", "bonus_200_yards")

    # ── Receiving ──────────────────────────────────────────────────────────────
    rec_yds  = val("receiving_yards")
    rec_tds  = val("receiving_tds")
    recs     = val("receptions")
    rec_fum  = val("receiving_fumbles_lost")
    rec_2pt  = val("receiving_2pt_conversions")

    ypp = cfg("receiving", "yards_per_point")
    if ypp > 0:
        total += rec_yds / ypp
    total += rec_tds * cfg("receiving", "td_points")
    total += recs    * cfg("receiving", "reception_bonus")
    total += rec_fum * cfg("receiving", "fumble_lost_deduction")  # negative
    total += rec_2pt * cfg("receiving", "two_pt_conversion")
    if rec_yds >= 100:
        total += cfg("receiving", "bonus_100_yards")
    if rec_yds >= 200:
        total += cfg("receiving", "bonus_200_yards")

    # ── Kicking [LIVE API] ─────────────────────────────────────────────────────
    total += val("pat_made")      * cfg("kicking", "pat_made")
    total += val("pat_missed")    * cfg("kicking", "pat_missed")
    total += val("fg_made_0_39")  * cfg("kicking", "fg_made_0_39")
    total += val("fg_made_40_49") * cfg("kicking", "fg_made_40_49")
    total += val("fg_made_50_plus") * cfg("kicking", "fg_made_50_plus")
    total += val("fg_missed_0_39")  * cfg("kicking", "fg_missed_0_39")
    total += val("fg_missed_40_49") * cfg("kicking", "fg_missed_40_49")
    total += val("fg_missed_50_plus") * cfg("kicking", "fg_missed_50_plus")

    # ── DST [LIVE API] ─────────────────────────────────────────────────────────
    total += val("dst_sacks")             * cfg("dst", "sack")
    total += val("dst_interceptions")     * cfg("dst", "interception")
    total += val("dst_fumbles_recovered") * cfg("dst", "fumble_recovered")
    total += val("dst_touchdowns")        * cfg("dst", "touchdown")
    total += val("dst_safeties")          * cfg("dst", "safety")
    total += val("dst_blocked_kicks")     * cfg("dst", "blocked_kick")
    total += val("dst_return_tds")        * cfg("dst", "return_td")
    total += val("dst_three_and_outs")    * cfg("dst", "three_and_out")
    total += val("dst_fourth_down_stops") * cfg("dst", "fourth_down_stop")

    # Points allowed tier — find the right bracket
    pts_allowed = stats.get("dst_points_allowed")
    if pts_allowed is not None:
        pa = float(pts_allowed)
        if pa == 0:
            total += cfg("dst", "points_allowed_0")
        elif pa <= 6:
            total += cfg("dst", "points_allowed_1_6")
        elif pa <= 13:
            total += cfg("dst", "points_allowed_7_13")
        elif pa <= 20:
            total += cfg("dst", "points_allowed_14_20")
        elif pa <= 27:
            total += cfg("dst", "points_allowed_21_27")
        elif pa <= 34:
            total += cfg("dst", "points_allowed_28_34")
        else:
            total += cfg("dst", "points_allowed_35_plus")

    # Yards allowed tier
    yds_allowed = stats.get("dst_yards_allowed")
    if yds_allowed is not None:
        ya = float(yds_allowed)
        if ya < 100:
            total += cfg("dst", "yards_allowed_0_99")
        elif ya < 200:
            total += cfg("dst", "yards_allowed_100_199")
        elif ya < 300:
            total += cfg("dst", "yards_allowed_200_299")
        elif ya < 400:
            total += cfg("dst", "yards_allowed_300_399")
        elif ya < 450:
            total += cfg("dst", "yards_allowed_400_449")
        elif ya < 500:
            total += cfg("dst", "yards_allowed_450_499")
        else:
            total += cfg("dst", "yards_allowed_500_plus")

    return round(total, 2)


def calculate_avg_points(weekly_stats: list[dict], scoring: dict) -> float:
    """
    Calculate average fantasy points per game from a list of weekly stat dicts.

    Args:
        weekly_stats: list of stat dicts from weekly_stats table
        scoring:      league scoring_config dict

    Returns:
        float: average points per game
    """
    if not weekly_stats:
        return 0.0

    totals = [calculate_points(row, scoring) for row in weekly_stats]
    return round(sum(totals) / len(totals), 2)
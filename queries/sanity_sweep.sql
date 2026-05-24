-- sanity_sweep.sql
-- 5 validation queries to verify data integrity across all three tables
-- Run after every ingestion to catch bad data early

-- ── Query 1: Row counts per table ─────────────────────────────────────────────
-- Expectation: all three tables have data, nothing is zero
SELECT 'schedules'    AS table_name, COUNT(*) AS row_count FROM schedules
UNION ALL
SELECT 'rosters',                    COUNT(*)              FROM rosters
UNION ALL
SELECT 'weekly_stats',               COUNT(*)              FROM weekly_stats;


-- ── Query 2: Season coverage check ────────────────────────────────────────────
SELECT 'schedules' AS table_name, season, COUNT(*) AS rows
FROM schedules GROUP BY season
UNION ALL
SELECT 'rosters', season, COUNT(*)
FROM rosters GROUP BY season
UNION ALL
SELECT 'weekly_stats', season, COUNT(*)
FROM weekly_stats GROUP BY season
ORDER BY table_name, season;


-- ── Query 3: Null check on critical columns ────────────────────────────────────
-- Expectation: zero nulls on columns that should always have values
SELECT
    'schedules.game_id'       AS check_col, COUNT(*) AS null_count FROM schedules    WHERE game_id IS NULL
UNION ALL
SELECT 'schedules.home_team',              COUNT(*) FROM schedules    WHERE home_team IS NULL
UNION ALL
SELECT 'schedules.away_team',              COUNT(*) FROM schedules    WHERE away_team IS NULL
UNION ALL
SELECT 'rosters.player_id',                COUNT(*) FROM rosters      WHERE player_id IS NULL
UNION ALL
SELECT 'rosters.team',                     COUNT(*) FROM rosters      WHERE team IS NULL
UNION ALL
SELECT 'weekly_stats.player_id',           COUNT(*) FROM weekly_stats WHERE player_id IS NULL
UNION ALL
SELECT 'weekly_stats.season',              COUNT(*) FROM weekly_stats WHERE season IS NULL
UNION ALL
SELECT 'weekly_stats.week',                COUNT(*) FROM weekly_stats WHERE week IS NULL;


-- ── Query 4: Week range check ─────────────────────────────────────────────────
-- Expectation: regular season weeks 1-18, no week 0 or week 99 weirdness
SELECT
    season,
    MIN(week) AS min_week,
    MAX(week) AS max_week,
    COUNT(DISTINCT week) AS distinct_weeks
FROM weekly_stats
WHERE season_type = 'REG'
GROUP BY season
ORDER BY season;


-- ── Query 5: Top fantasy scorers sanity check ─────────────────────────────────
-- Expectation: recognizable player names, reasonable point totals (no 9999s)
SELECT
    player_name,
    season,
    ROUND(SUM(fantasy_points_ppr)::numeric, 1) AS total_ppr_points
FROM weekly_stats
WHERE season_type = 'REG'
GROUP BY player_name, season
ORDER BY total_ppr_points DESC
LIMIT 10;
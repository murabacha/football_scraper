Database design for Football Scraper

This document describes the database schema used by the Scrapy project located in `football_scraper`. It documents table definitions, columns, types, relationships, common queries, recommended indexes, and suggested improvements (migrations, data normalization).

Overview
--------
The scrapy pipeline (`pipelines.py`) persists scraped match data into a MySQL database (SQLAlchemy + pymysql). The schema consists of three main tables:

- `matches` — one row per match (basic match info)
- `match_events` — one row per event (goal, card, substitution, ...), references `matches`
- `match_stats` — one row per match summarizing statistics (possession, shots, etc.), references `matches`

These are simple, denormalized tables designed for fast insertion and straightforward queries to retrieve match, event, and stats data.

Current table definitions (as used in `pipelines.py`)
---------------------------------------------------
The pipeline defines tables using SQLAlchemy `Table` objects. The following SQL-like definitions show the same schema.

-- `matches`
CREATE TABLE matches (
  id INT PRIMARY KEY AUTO_INCREMENT,
  league VARCHAR(255) NOT NULL,
  hometeam VARCHAR(255),
  awayteam VARCHAR(255),
  hometeam_goals INT,
  awayteam_goals INT,
  kickoff VARCHAR(255), -- stored as string in current implementation
  match_url VARCHAR(500) -- pipeline stores a URL id (last path segment) by default
);

-- `match_events`
CREATE TABLE match_events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  match_id INT,
  team VARCHAR(255),
  minute INT,
  type VARCHAR(100),
  player_in VARCHAR(255),
  player_out VARCHAR(255),
  scorer VARCHAR(255),
  assist VARCHAR(255),
  player VARCHAR(255),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- `match_stats`
CREATE TABLE match_stats (
  id INT PRIMARY KEY AUTO_INCREMENT,
  match_id INT,
  possession_home VARCHAR(50),
  possession_away VARCHAR(50),
  total_shots_home INT,
  total_shots_away INT,
  shots_on_target_home INT,
  shots_on_target_away INT,
  duels_won_home VARCHAR(50),
  duels_won_away VARCHAR(50),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

Notes about current implementation
----------------------------------
- `match_url`: the pipeline takes `match_url` from the item and transforms it with `url.split('/')[-1]`. That means only the final path segment (a match id string) is stored. If you want the full URL, store `response.url` directly and avoid splitting.
- `kickoff` is stored as a string (`VARCHAR`) and the spider currently writes either a page-provided value or a fallback `current_date_string`. That can lead to inconsistent formats (e.g., '2025-11-02', '2 Nov 2025 19:30', or None).
- Some stat fields (e.g., `possession_home`) are stored as strings like "54% 46%" in the spider. The pipeline maps these fields into the `match_stats` table without normalization.

Recommended schema improvements
-------------------------------
If you plan to query/aggregate by time or want stricter data integrity, consider the following improvements.

1) Normalize `kickoff` to DATETIME (or DATE) and store a consistent format.
   - Change column type to `DATETIME` (or `DATE`) depending on whether you have time data.
   - Parse the spider's extracted `kickoff` strings into a Python `datetime` before inserting.

Example migration SQL (manual):
ALTER TABLE matches ADD COLUMN kickoff_dt DATETIME NULL;
-- populate kickoff_dt from existing kickoff strings where possible (requires parsing)
-- after validation, drop old kickoff and rename kickoff_dt -> kickoff

2) Use indexes for faster lookups
   - `match_url` is used to check for existing matches. Add an index or unique constraint on it:
     ALTER TABLE matches ADD UNIQUE INDEX ux_matches_match_url (match_url(255));
   - Add an index on `kickoff` if you will frequently query by date:
     CREATE INDEX idx_matches_kickoff ON matches(kickoff);
   - Add an index on `match_events.match_id` and `match_stats.match_id` (MySQL adds indexes for FK in some setups, but explicitly adding them is safe):
     CREATE INDEX idx_match_events_match_id ON match_events(match_id);
     CREATE INDEX idx_match_stats_match_id ON match_stats(match_id);

3) Make numeric stat types consistent
   - Right now `total_shots_home` etc. are stored as INT. Ensure the spider stores clean integers (strip extra text). If the spider stores composite strings ("12 (4)") or ranges, consider storing raw strings in a separate column and parsed ints in typed columns.

4) Add NOT NULL and CHECK constraints where appropriate
   - `league` is currently created as NOT NULL in the pipeline. Consider adding NOT NULL or CHECKs for other columns if your data quality allows it.

Sample CREATE TABLE statements with suggested changes
----------------------------------------------------
-- Matches with a proper DATETIME kickoff and unique match_url
CREATE TABLE matches (
  id INT PRIMARY KEY AUTO_INCREMENT,
  league VARCHAR(255) NOT NULL,
  hometeam VARCHAR(255),
  awayteam VARCHAR(255),
  hometeam_goals INT,
  awayteam_goals INT,
  kickoff DATETIME,
  match_url VARCHAR(500),
  UNIQUE KEY ux_matches_match_url (match_url(255))
);

CREATE TABLE match_events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  match_id INT NOT NULL,
  team VARCHAR(50),
  minute INT,
  type VARCHAR(100),
  player_in VARCHAR(255),
  player_out VARCHAR(255),
  scorer VARCHAR(255),
  assist VARCHAR(255),
  player VARCHAR(255),
  INDEX idx_match_events_match_id (match_id),
  FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE
);

CREATE TABLE match_stats (
  id INT PRIMARY KEY AUTO_INCREMENT,
  match_id INT NOT NULL,
  possession_home VARCHAR(50),
  possession_away VARCHAR(50),
  total_shots_home INT,
  total_shots_away INT,
  shots_on_target_home INT,
  shots_on_target_away INT,
  duels_won_home VARCHAR(50),
  duels_won_away VARCHAR(50),
  INDEX idx_match_stats_match_id (match_id),
  FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE
);

Example queries
---------------
-- Get the last 10 matches and their kickoff
SELECT id, hometeam, awayteam, kickoff FROM matches ORDER BY kickoff DESC LIMIT 10;

-- Get events for a specific match
SELECT e.* FROM match_events e WHERE e.match_id = 123 ORDER BY minute;

-- Join match with its stats
SELECT m.id, m.hometeam, m.awayteam, s.possession_home, s.total_shots_home
FROM matches m
JOIN match_stats s ON s.match_id = m.id
WHERE m.kickoff BETWEEN '2025-08-01' AND '2025-08-31'
ORDER BY m.kickoff;

-- Aggregate total goals by team in a date range (requires hometeam_goals and awayteam_goals to be ints)
SELECT hometeam AS team, SUM(hometeam_goals) AS goals FROM matches WHERE kickoff BETWEEN '2025-08-01' AND '2025-08-31' GROUP BY hometeam
UNION
SELECT awayteam AS team, SUM(awayteam_goals) AS goals FROM matches WHERE kickoff BETWEEN '2025-08-01' AND '2025-08-31' GROUP BY awayteam;

Operational notes and best practices
-----------------------------------
- Transactions: when saving a match and related rows (events, stats) consider wrapping the inserts in a single transaction so that partial writes don't occur if something fails. SQLAlchemy `engine.begin()` is already used in the pipeline — good.

- Idempotency: the current pipeline checks for an existing match by `match_url` and skips insert if present. Ensure that `match_url` values are consistent across runs (either always full URL or always the same path segment) so duplicates are reliably detected.

- Character sets and encoding: if match/team/player names contain non-ASCII characters, ensure the DB and client use UTF-8 (utf8mb4) character set.

- Backups and migrations: when changing types (e.g., `kickoff` -> DATETIME), export current data and run conversion scripts to safely populate the new column before dropping the old one.

Debugging tips
--------------
- If fields are unexpectedly NULL in DB, log the item before insertion to inspect what the spider produced.
- Add debug logs in the pipeline showing the `match_url` and `kickoff` value used for insert.
- If your queries are slow, check missing indexes (use `EXPLAIN` for slow queries).

Next steps I can help with
-------------------------
- Implement the migration to change `kickoff` from `VARCHAR` to `DATETIME` and update the spider/pipeline to produce normalized datetimes.
- Add indices and unique constraints via SQLAlchemy in the pipeline and apply them safely.
- Improve idempotency by storing the full `match_url` or a consistent external match id and adding a unique constraint.

If you'd like, I can also update the pipeline code to:
- parse kickoff into a Python datetime (using dateutil or custom parsing),
- insert the parsed value into a `DATETIME` column,
- add an index on `match_url`, and
- demonstrate a migration snippet that safely upgrades existing data.

---
File created: `DATABASE.md` in the project folder.
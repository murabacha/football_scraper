Football Scraper — Documentation

This README documents the main parts of the small Scrapy project so you can share it with friends. It focuses on the necessary files that implement scraping and saving match data:

- `items.py`
- `spiders/ball_scraper.py`
- `pipelines.py`

The doc covers: what each file does, the data flow, the DB schema used, how to run the spider, common bugs and fixes, and suggestions for improvements.

## 1 — High level overview

The project is a Scrapy-based web scraper that visits OneFootball match pages and extracts:
- teams and scores
- match events (goals, substitutions, cards, etc.)
- match statistics (possession, shots, duels won)
- kickoff and stadium info

Each match is represented by a `FootballScraperItem` (see `items.py`). Items are yielded by the spider and passed through pipelines which (1) normalize/clean data and (2) save it into a MySQL database using SQLAlchemy.

## 2 — Files and responsibilities

### `items.py`
Defines the item shape used by the spider:
- Fields: `league`, `hometeam`, `awayteam`, `hometeam_goals`, `awayteam_goals`, `events`, `possession_Home`, `Possession_Away`, `Total_shots_Home`, `Total_shots_Away`, `Shots_on_target_Home`, `Shots_on_target_Away`, `Duels_won_Home`, `Duels_won_Away`, `kickoff`, `stadium`, `match_url`.

Purpose: gives a structured container that the spider fills and the pipelines consume.

### `spiders/ball_scraper.py`
Primary scraper. Key behavior:
- Entry URL(s) in `start_urls` (e.g. `https://onefootball.com/en/matches?date=2025-11-02`).
- `parse` extracts links to individual match pages from `__NEXT_DATA__` JSON and yields requests to `parse_stats`.
- `parse_stats` (for each match page):
  - Creates a fresh `FootballScraperItem` instance per match.
  - Extracts `match_url` (page URL), `league`, `hometeam`, `awayteam`, `hometeam_goals`, `awayteam_goals`.
  - Builds an `events` list from home and away event nodes; event entries include: `team`, `minute`, `type`, `player_in`, `player_out`, `scorer`, `assist`, `player`.
  - Extracts match statistics (possession, shots, shots on target, duels won) from stat nodes and stores into fields like `possession_Home`, `Total_shots_Home`, etc.
  - Extracts extra info like kickoff date/time and stadium from a `MatchInfoEntry_subtitle` selector. If page fields are missing, the spider may fall back to `self.current_date`.
  - Yields the filled `FootballScraperItem`.

Important implementation notes / pitfalls seen in the codebase:
- Make a new `FootballScraperItem()` inside `parse_stats` for each match (not a class-level shared instance). If shared, different matches will overwrite the same item leading to wrong data in DB.
- Ensure the code that extracts statistics and kickoff runs once per match (not inside an events loop). If it's inside the away-events loop and a match has zero away events, kickoff/stats may never be set.

### `pipelines.py`
There are three pipeline classes of interest:

1. `FootballScraperPipeline`:
   - Ensures `events` is present and non-empty; if empty, inserts a placeholder single event with all fields `None`.

2. `CleanEventMinutesPipeline`:
   - Iterates events and normalizes the `minute` field.
   - Removes apostrophes, strips whitespace, pads single-digit minutes with a leading zero, converts numeric minute strings to `int`, else sets `minute` to `None`.

3. `SaveMatchesToDatabase`:
   - Uses SQLAlchemy + `pymysql` to connect to a MySQL database at `mysql+pymysql://root:robert@localhost/football` (change credentials/host as needed).
   - Defines three tables using SQLAlchemy `Table` objects:
     - `matches` (id, league, hometeam, awayteam, hometeam_goals, awayteam_goals, kickoff, match_url)
     - `match_events` (id, match_id -> matches.id, team, minute, type, player_in, player_out, scorer, assist, player)
     - `match_stats` (id, match_id -> matches.id, possession_home, possession_away, total_shots_home/away, shots_on_target_home/away, duels_won_home/away)
   - Insert flow per item:
     1. Compute `url_id` by splitting `match_url` at the last `/` and taking the last part. Query to see if `matches.match_url == url_id` exists; skip if already exists.
     2. Insert into `matches` table and get `match_id` from `result.inserted_primary_key[0]`.
     3. Insert one row per event into `match_events` with `match_id` foreign key.
     4. Insert aggregated stats into `match_stats` with `match_id`.
   - Note: `kickoff` is stored as a plain string in `matches.kickoff`. Consider using a proper datetime/datetimestamp type if standardization is required.

## 3 — Data flow (short)
1. Spider requests match page -> `parse_stats` builds `FootballScraperItem`.
2. Item passes to pipelines in configured order:
   - `FootballScraperPipeline` (ensure `events` non-empty)
   - `CleanEventMinutesPipeline` (normalize event minutes)
   - `SaveMatchesToDatabase` (persist match, events, stats to MySQL)

## 4 — How to run
From the project root (where `scrapy.cfg` lives, or inside `football_scraper` package if you run that way):

```powershell
scrapy crawl ball_scraper
```

Database setup:
- Ensure MySQL is running and a database named `football` exists.
- Update DB credentials in `pipelines.py` (the SQLAlchemy URL) if different from `root:robert@localhost`.
- The pipeline will create tables automatically (via `metadata.create_all(self.engine)`).

## 5 — Common issues and fixes

1) All matches share event/stats from first match
   - Cause: a single `FootballScraperItem` instance declared on the spider class (class-level attribute) gets reused across matches.
   - Fix: create `FootballScraperItem()` inside `parse_stats` for each request (one item per match) and only yield that new instance.

2) `kickoff` stored as `NULL` for some matches
   - Cause: the block that extracts kickoff/stats was placed inside a loop over events (for example inside the away-team events loop). If there are no away events that loop body never runs, so the code that sets `kickoff` never executes.
   - Fix: extract match-level info (stats, kickoff, stadium) once per match after building events, not inside an events loop. Add fallback logic: try `extra_info` page values, else fall back to `self.current_date` or `None`.

3) Mismatched keys between spider and pipeline
   - Double-check the capitalization and exact field names. Example: the spider sets `possession_Home` while pipeline inserts `possession_Home`/`Possession_Away`. Keep naming consistent to avoid `None` values in DB.

4) Datetime consistency
   - Kickoff is currently saved as a string. For consistent querying and sorting, parse kickoff into a standard format (ISO 8601) and store as `DATETIME` in DB. That requires parsing strings like `2 Nov 2025 19:30` to a Python `datetime`.

## 6 — Debugging tips
- Add a log line at the end of `parse_stats` to print the item before yielding:
  ```python
  self.logger.info(f"Item for {ball_item.get('hometeam')} vs {ball_item.get('awayteam')}: kickoff={ball_item.get('kickoff')}")
  ```
- Add `spider.logger.info` messages in `SaveMatchesToDatabase.process_item` to show `match_id` and the `kickoff` value that will be inserted.
- Temporarily write one scraped page to disk and inspect selectors with `response.css(...).getall()` in the Scrapy shell.

## 7 — Suggested improvements (next steps)
- Normalize `kickoff` into an ISO datetime and change DB column to `DATETIME`.
- Use an `ItemLoader` in the spider for cleaner extraction and default handling.
- Add more robust error handling around the DB inserts and use a single transaction to insert match/events/stats together.
- Add tests or an example HTML file + a small test harness that runs `parse_stats` against saved HTML and asserts expected item fields.
- Consider storing `match_url` as the full URL instead of the split `url_id`, or store both (full and short id) for clarity.

## 8 — Where I can help next
- Normalize kickoff datetimes and update the DB schema.
- Add debug logging and a small test to verify multiple matches behave correctly.
- Rework the pipeline to use SQLAlchemy ORM models instead of manual `Table` inserts if you prefer objects and relationships.

---
If you want, I can commit a `README.md` (this file) into the repo (already created here) and also add a short `USAGE.md` or a small script which will query the DB and print the last 10 matches for quick verification. Tell me which follow-up you'd like.
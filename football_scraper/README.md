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
- Fields: `league`, `hometeam`, `hometeam_logo`, `awayteam`, `awayteam_logo`, `hometeam_goals`, `awayteam_goals`, `events`, `possession_Home`, `Possession_Away`, `Total_shots_Home`, `Total_shots_Away`, `Shots_on_target_Home`, `Shots_on_target_Away`, `Duels_won_Home`, `Duels_won_Away`, `kickoff`, `stadium`, `match_url`, `match_lineup`, `match_completion`, `match_time`, `game_time`.

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
  - Extracts team lineups, including players, jersey numbers, and formation, into the `match_lineup` field.
  - Yields the filled `FootballScraperItem`.



### `pipelines.py`
There are three pipeline classes of interest:

1. `FootballScraperPipeline`:
   - Cleans and provides default values for several fields.
   - If `events` is empty, it inserts a placeholder event.
   - If `stadium` is missing, it sets a default.
   - If `match_lineup` is empty, it creates placeholder entries for home and away teams.
   - Normalizes `hometeam_goals` and `awayteam_goals` to integers, defaulting to 0.

2. `CleanEventMinutesPipeline`:
   - Iterates events and normalizes the `minute` field.
   - It cleans string values (like "45+1'") into integers.

3. `SaveMatchesToDatabase`:
   - Connects to a MySQL database (credentials are in the `create_engine` call).
   - Defines four tables using SQLAlchemy `Table` objects:
     - `matches` (with all match-level details)
     - `match_events` (id, match_id -> matches.id, team, minute, type, player_in, player_out, scorer, assist, player)
     - `match_stats` (id, match_id -> matches.id, possession_home, possession_away, total_shots_home/away, shots_on_target_home/away, duels_won_home/away)
     - `match_lineups` (id, match_id -> matches.id, team, formation, lineup)
   - Insert flow per item:
     1. Checks if a match exists based on `match_url`.
     2. If the match is new, it inserts a new record into `matches`.
     3. If the match exists, it compares the scraped data with the stored data and updates the `matches` record if anything has changed.
     4. It synchronizes `match_events` and `match_lineups`, only inserting new events or lineups that are not already in the database for that match.
     5. It inserts or updates the record in `match_stats`.

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
- Update DB credentials in `pipelines.py` (the SQLAlchemy `create_engine` URL).
- The pipeline will create tables automatically (via `metadata.create_all(self.engine)`).

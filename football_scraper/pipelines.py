# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FootballScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        names = ['events',]
        for name in names:
            value = adapter.get(name)
            if len(value) == 0:
                events = [
                    {
                        "team": None,
                        "minute": None,
                        "type": None,
                        "scorer": None,
                        "assist": None,
                        "player": None,
                        "player_in": None,
                        "player_out": None,
                    }
                ]
                adapter[name] = events
        stadium = adapter.get('stadium')
        if stadium is None:
            adapter['stadium'] = 'Unknown Stadium'
        
    
        lineups = adapter.get('match_lineup')
        cleaned_lineups = []
        if len(lineups ) == 0:
            lineups = [{
                "team": adapter.get('hometeam'),
                "lineup": 'no available lineup',
                "home_formation": 'Unknown Formation',
            },
            {
                "team": adapter.get('awayteam'),
                "lineup": 'no available lineup',
                "away_formation": 'Unknown Formation',
            }]
            for lineup in lineups:
                cleaned_lineups.append(lineup)
            adapter['match_lineup'] = cleaned_lineups
            return item
        
        for lineup in lineups:
            try:
                home_formation = lineup['home_formation']
                players_lineup = lineup.get('lineup')
                if home_formation is None and players_lineup is None:
                    lineup['home_formation'] = 'Unknown Formation'
                    lineup['lineup'] = 'no available lineup'
                elif home_formation is None and players_lineup is not None:
                    lineup['home_formation'] = 'Unknown Formation'
                    lineup['lineup'] = players_lineup
                elif home_formation is not None and players_lineup is None:
                    lineup['lineup'] = 'no available lineup'
                    lineup['home_formation'] = home_formation
                cleaned_lineups.append(lineup)
            except Exception as e:
                continue
        for lineup in lineups:
            try:
                away_formation = lineup['away_formation']
                players_lineup = lineup.get('lineup')
                if away_formation is None and players_lineup is None:
                    lineup['away_formation'] = 'Unknown Formation'
                    lineup['lineup'] = 'no available lineup'
                elif away_formation is None and players_lineup is not None:
                    lineup['away_formation'] = 'Unknown Formation'
                    lineup['lineup'] = players_lineup
                elif away_formation is not None and players_lineup is None:
                    lineup['lineup'] = 'no available lineup'
                    lineup['away_formation'] = away_formation
                cleaned_lineups.append(lineup)
            except Exception as e:
                continue
            
        adapter['match_lineup'] = cleaned_lineups
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print(adapter.get('match_lineup'))
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        names = ['hometeam_goals', 'awayteam_goals']
        for name in names:
            value = adapter.get(name)
            if value is None:
                adapter[name] = 0
            elif value == '-':
                adapter[name] = 0
            adapter[name] = int(value) if value is not None and value.isdigit() else 0


        return item




class CleanEventMinutesPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        event_list = adapter.get('events')
        for event in event_list:
            event_keys = event.keys()
            for key in event_keys:
                if key == 'minute':
                    uncleaned_minute = event[key] 
                    if type(uncleaned_minute) == int:
                        event['minute'] = uncleaned_minute
                    else:
                        if uncleaned_minute is None:
                            event['minute'] = None
                        else:
                            cleaned_minute = uncleaned_minute.replace("'", "").strip() 
                            if cleaned_minute and cleaned_minute.isdigit():
                                event['minute'] = int(cleaned_minute)
                            else:
                                event['minute'] = None
        return item


from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, Date, select
import pymysql
import json
class SaveMatchesToDatabase:
    def __init__(self):
        
        self.connect_args = {'ssl':{'mode':'REQUIRED'}}
        self.engine = create_engine('mysql+pymysql://avnadmin:AVNS_TTsiC2_1m5LG1Uh7112@robert-football-database2025-robertthuo2004-f295.i.aivencloud.com:26666/football_data',connect_args = self.connect_args)
        #self.engine  = create_engine('mysql+pymysql://root:robert@localhost/football')
        self.metadata = MetaData()
        self.matches = Table('matches', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('league', String(255), nullable=False,default='Unknown League'),
            Column('hometeam', String(255)),
            Column('awayteam', String(255)),
            Column('hometeam_logo', String(500)),
            Column('awayteam_logo', String(500)),
            Column('hometeam_goals', String(50)),
            Column('awayteam_goals', String(50)),
            Column('kickoff', Date),
            Column('match_url', String(500)),
            Column('match_completion', String(500)),
            Column('stadium',String(500)),
            Column('match_time', String(500)),
            Column('game_time', String(500)),
        )
        self.match_events = Table('match_events', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('match_id', Integer, ForeignKey('matches.id')),
            Column('team', String(255)),
            Column('minute', Integer),
            Column('type', String(100)),
            Column('player_in', String(255)),
            Column('player_out', String(255)),
            Column('scorer', String(255)),
            Column('assist', String(255)),
            Column('player', String(255)),
        )
        self.match_stats = Table('match_stats', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('match_id', Integer, ForeignKey('matches.id')),
            Column('possession_home', String(50)),
            Column('possession_away', String(50)),
            Column('total_shots_home', String(50)),
            Column('total_shots_away', String(50)),
            Column('shots_on_target_home', String(50)),
            Column('shots_on_target_away', String(50)),
            Column('duels_won_home', String(50)),
            Column('duels_won_away', String(50)),
        )
        self.match_lineups = Table('match_lineups', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('match_id', Integer, ForeignKey('matches.id')),
            Column('team', String(255)),
            Column('lineup', String(2000)),
            Column('formation', String(50)),
        )
        self.metadata.create_all(self.engine)
        self.connection = self.engine.connect()

    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url_id = adapter.get("match_url").split("/")[-1]

        # Check if match exists
        with self.engine.begin() as conn:
            existing = conn.execute(
                select(self.matches).where(self.matches.c.match_url == url_id)
            ).fetchone()

        scraped_data = {
            "league": adapter.get("league"),
            "hometeam": adapter.get("hometeam"),
            "awayteam": adapter.get("awayteam"),
            "hometeam_logo": adapter.get("hometeam_logo"),
            "awayteam_logo": adapter.get("awayteam_logo"),
            "hometeam_goals": adapter.get("hometeam_goals"),
            "awayteam_goals": adapter.get("awayteam_goals"),
            "kickoff": adapter.get("kickoff"),
            "match_url": url_id,
            "match_completion": adapter.get("match_completion"),
            "stadium": adapter.get("stadium"),
            "match_time": adapter.get("match_time"),
            "game_time": adapter.get("game_time"),
        }

        if not existing:
            spider.logger.info(f"Inserting new match: {adapter.get('hometeam')} vs {adapter.get('awayteam')}")
            with self.engine.begin() as conn:
                result = conn.execute(self.matches.insert().values(**scraped_data))
                match_id = result.inserted_primary_key[0]
        else:
            match_id = existing.id
            # Compare and update if any field differs
            db_data = dict(existing._mapping)
            if not scraped_data.get('match_time'):
                scraped_data['match_time'] = db_data.get('match_time')
            changed = any(str(db_data[k]) != str(v) for k, v in scraped_data.items())
            if changed:
                spider.logger.info(f"Updating match data for {adapter.get('hometeam')} vs {adapter.get('awayteam')}")
                with self.engine.begin() as conn:
                    conn.execute(
                        self.matches.update().where(self.matches.c.id == match_id).values(**scraped_data)
                    )

        self.sync_match_events(match_id, adapter, spider)
        self.sync_match_lineups(match_id, adapter, spider)

        self.upsert_stats(match_id, adapter, spider)

        return item

    def sync_match_events(self, match_id, adapter, spider):
        events = adapter.get("events", [])
        if not events:
            return

        with self.engine.begin() as conn:
            existing = conn.execute(
                select(self.match_events).where(self.match_events.c.match_id == match_id)
            ).fetchall()

            existing_keys = {
                (r.team, r.minute, r.type, r.player_in, r.player_out, r.scorer, r.assist, r.player)
                for r in existing
            }

            for ev in events:
                key = (
                    ev.get("team"), ev.get("minute"), ev.get("type"),
                    ev.get("player_in"), ev.get("player_out"),
                    ev.get("scorer"), ev.get("assist"), ev.get("player")
                )
                if key not in existing_keys:
                    conn.execute(self.match_events.insert().values(match_id=match_id, **ev))
                    spider.logger.info(f"Inserted new event: {ev.get('type')} ({ev.get('team')}) min {ev.get('minute')}")

    def sync_match_lineups(self, match_id, adapter, spider):
        lineups = adapter.get("match_lineup", [])
        if not lineups:
            return

        with self.engine.begin() as conn:
            existing = conn.execute(
                select(self.match_lineups).where(self.match_lineups.c.match_id == match_id)
            ).fetchall()

            existing_keys = {
                (r.team, r.formation, r.lineup)
                for r in existing
            }

            for lineup in lineups:
                team = lineup.get("team")
                formation = lineup.get("home_formation") or lineup.get("away_formation")
                lineup_json = json.dumps(lineup.get("lineup")) if isinstance(lineup.get("lineup"), list) else lineup.get("lineup")
                key = (team, formation, lineup_json)
                if key not in existing_keys:
                    conn.execute(self.match_lineups.insert().values(
                        match_id=match_id,
                        team=team,
                        formation=formation,
                        lineup=lineup_json
                    ))
                    spider.logger.info(f"Inserted new lineup for {team}")
    def upsert_stats(self, match_id, adapter, spider):
        stats_data = {
            "match_id": match_id,
            "possession_home": adapter.get("possession_Home"),
            "possession_away": adapter.get("Possession_Away"),
            "total_shots_home": adapter.get("Total_shots_Home"),
            "total_shots_away": adapter.get("Total_shots_Away"),
            "shots_on_target_home": adapter.get("Shots_on_target_Home"),
            "shots_on_target_away": adapter.get("Shots_on_target_Away"),
            "duels_won_home": adapter.get("Duels_won_Home"),
            "duels_won_away": adapter.get("Duels_won_Away"),
        }

        with self.engine.begin() as conn:
            existing = conn.execute(
                select(self.match_stats).where(self.match_stats.c.match_id == match_id)
            ).fetchone()
            if not existing:
                conn.execute(self.match_stats.insert().values(**stats_data))
            else:
                conn.execute(
                    self.match_stats.update().where(self.match_stats.c.match_id == match_id).values(**stats_data)
                )
   
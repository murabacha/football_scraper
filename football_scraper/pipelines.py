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


from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
import pymysql
import json
class SaveMatchesToDatabase:
    def __init__(self):
        
        self.connect_args = {'ssl':{'mode':'REQUIRED'}}
        self.engine = create_engine('mysql+pymysql://(your logins of the database here )',connect_args = self.connect_args)
        self.metadata = MetaData()
        self.matches = Table('matches', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('league', String(255), nullable=False,default='Unknown League'),
            Column('hometeam', String(255)),
            Column('awayteam', String(255)),
            Column('hometeam_goals', Integer),
            Column('awayteam_goals', Integer),
            Column('kickoff', String(255)),
            Column('match_url', String(500)),
            Column('match_completion', String(500)),
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
            Column('total_shots_home', Integer),
            Column('total_shots_away', Integer),
            Column('shots_on_target_home', Integer),
            Column('shots_on_target_away', Integer),
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
        url = adapter.get('match_url')
        url_id = url.split('/')[-1]
        existing_match = self.matches.select().where(
            (self.matches.c.match_url == url_id)
        )
        with self.engine.begin() as conn:
            try:
                existing_result = conn.execute(existing_match).fetchone()
            except Exception as e:
                spider.logger.error(f"Database query failed: {e}")
                existing_result = None
        if existing_result:
            spider.logger.info(f"Match already exists in database: {adapter.get('hometeam')} vs {adapter.get('awayteam')}")
            return item
        
        ins = self.matches.insert().values(
            league=adapter.get('league'),
            hometeam=adapter.get('hometeam'),
            awayteam=adapter.get('awayteam'),
            hometeam_goals=adapter.get('hometeam_goals'),
            awayteam_goals=adapter.get('awayteam_goals'),
            kickoff=adapter.get('kickoff'),
            match_url=url_id,
            match_completion=adapter.get('match_completion'),
        )
        with self.engine.begin() as conn:
            result = conn.execute(ins)
            match_id = result.inserted_primary_key[0]# will get the inserted match id which is auto incremented on the database side(retuns tuple hence the index [0])
        print('*************************************************************************************')
        spider.logger.info(f"Inserted match: {adapter.get('hometeam')} vs {adapter.get('awayteam')}")

        event_list = adapter.get('events')
        for event in event_list:
            ins_event = self.match_events.insert().values(
                match_id=match_id,
                team=event.get('team'),
                minute=event.get('minute'),
                type=event.get('type'),
                player_in=event.get('player_in'),
                player_out=event.get('player_out'),
                scorer=event.get('scorer'),
                assist=event.get('assist'),
                player=event.get('player'),
            )
            with self.engine.begin() as conn:
                conn.execute(ins_event)
            print('-------------------------------------------------------------------------------------')
            spider.logger.info(f"Inserted event: {event.get('type')} at minute {event.get('minute')}")

        ins_stats = self.match_stats.insert().values(
            match_id=match_id,
            possession_home=adapter.get('possession_Home'),
            possession_away=adapter.get('Possession_Away'),            
            total_shots_home=adapter.get('Total_shots_Home'),
            total_shots_away=adapter.get('Total_shots_Away'),
            shots_on_target_home=adapter.get('Shots_on_target_Home'),
            shots_on_target_away=adapter.get('Shots_on_target_Away'),
            duels_won_home=adapter.get('Duels_won_Home'),
            duels_won_away=adapter.get('Duels_won_Away'),
        )
        with self.engine.begin() as conn:
            conn.execute(ins_stats)
        lineups = adapter.get('match_lineup')
        for lineup in lineups:
            ins_lineup = self.match_lineups.insert().values(
                match_id=match_id,
                team=lineup.get('team'),
                lineup=json.dumps(lineup.get('lineup')),
                formation=lineup.get('home_formation') or lineup.get('away_formation'),
            )
            with self.engine.begin() as conn:
                conn.execute(ins_lineup)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        spider.logger.info(f"Inserted stats for match ID: {match_id}"
        )
        return item


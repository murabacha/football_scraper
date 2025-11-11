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
                    lineup['home_formation'] = 'Unknown Formation'
                    lineup['lineup'] = 'no available lineup'
                elif away_formation is None and players_lineup is not None:
                    lineup['home_formation'] = 'Unknown Formation'
                    lineup['lineup'] = players_lineup
                elif away_formation is not None and players_lineup is None:
                    lineup['lineup'] = 'no available lineup'
                    lineup['home_formation'] = away_formation
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


from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, Date
import pymysql
import json
class SaveMatchesToDatabase:
    def __init__(self):
        
        self.connect_args = {'ssl':{'mode':'REQUIRED'}}
        #self.engine = create_engine('mysql+pymysql://avnadmin:AVNS_TTsiC2_1m5LG1Uh7112@robert-football-database2025-robertthuo2004-f295.i.aivencloud.com:26666/football_data',connect_args = self.connect_args)
        self.engine  = create_engine('mysql+pymysql://root:robert@localhost/football')
        self.metadata = MetaData()
        self.matches = Table('matches', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('league', String(255), nullable=False,default='Unknown League'),
            Column('hometeam', String(255)),
            Column('awayteam', String(255)),
            Column('hometeam_logo', String(500)),
            Column('awayteam_logo', String(500)),
            Column('hometeam_goals', Integer),
            Column('awayteam_goals', Integer),
            Column('kickoff', Date),
            Column('match_url', String(500)),
            Column('match_completion', String(500)),
            Column('stadium',String(500)),
            #Column('match_time', String(500)),
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
            if existing_result.league == adapter.get('league') and existing_result.hometeam == adapter.get('hometeam') and existing_result.awayteam == adapter.get('awayteam')\
                  and existing_result.kickoff == adapter.get('kickoff') and existing_result.stadium == adapter.get('stadium') and existing_result.match_completion == adapter.get('match_completion'):
                spider.logger.info(f"Match already exists: {adapter.get('hometeam')} vs {adapter.get('awayteam')}")
                return item
            else:
                update_match = self.matches.update().where(self.matches.c.id == existing_result.id).values(
                league=adapter.get('league'),
                hometeam=adapter.get('hometeam'),
                awayteam=adapter.get('awayteam'),
                hometeam_logo=adapter.get('hometeam_logo'),
                awayteam_logo=adapter.get('awayteam_logo'),
                hometeam_goals=adapter.get('hometeam_goals'),
                awayteam_goals=adapter.get('awayteam_goals'),
                kickoff=adapter.get('kickoff'),
                match_url=url_id,
                match_completion=adapter.get('match_completion'),
                stadium=adapter.get('stadium')
            )
            with self.engine.begin() as conn:
                result = conn.execute(update_match)
                match_id = result.inserted_primary_key[0]#
            #get the events and lineups and stats
            event_list = adapter.get('events')
            def update_event(event):
                update_event = self.match_events.insert().values(
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
                        result = conn.execute(update_event)
                        return result
            for event in event_list:
                existing_event = self.match_events.select().where(
                    (self.match_events.c.match_id == match_id)
                )
                with self.engine.begin() as conn:
                    try:
                        existing_results = conn.execute(existing_event).fetchall()
                    except Exception as e:
                        spider.logger.error(f"Database query failed: {e}")
                        existing_result = None
                if existing_results:
                    for existing_result in existing_results:
                        event_type = existing_results.type
                        if event_type == 'Goal' or  event_type == 'Penalty' or event_type == 'Penalty Missed':
                            if event_type == adapter.get('type') and event.get('minute') == existing_result.minute and event.get('team') == existing_result.team and event.get('scorer') == existing_result.scorer:
                                continue
                            else:
                                update_event(event) 
                        elif event_type == 'Yellow card' or event_type == 'Red card' or event_type == 'Own goal':
                            if event_type == adapter.get('type') and event.get('minute') == existing_result.minute and event.get('team') == existing_result.team and event.get('player') == existing_result.player:
                                continue
                            else:
                                update_event(event) 
                        elif event_type == 'Substitution':
                            if event_type == adapter.get('type') and event.get('minute') == existing_result.minute and event.get('player_in') == existing_result.player_in and event.get('player_out') == existing_result.player_out:
                                continue
                            else:
                                update_event(event) 

                    else:
                        update_event(event)
                else:
                    update_event(event)
        else:
                    
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
                    result = conn.execute(ins_event)


            # return item
             
        
        ins = self.matches.insert().values(
            league=adapter.get('league'),
            hometeam=adapter.get('hometeam'),
            awayteam=adapter.get('awayteam'),
            hometeam_logo=adapter.get('hometeam_logo'),
            awayteam_logo=adapter.get('awayteam_logo'),
            hometeam_goals=adapter.get('hometeam_goals'),
            awayteam_goals=adapter.get('awayteam_goals'),
            kickoff=adapter.get('kickoff'),
            match_url=url_id,
            match_completion=adapter.get('match_completion'),
            stadium=adapter.get('stadium')
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
                lineup=json.dumps(lineup.get('lineup')) if lineup.get('lineup') != 'no available lineup' else lineup.get('lineup'),
                formation=lineup.get('home_formation') or lineup.get('away_formation'),
            )
            with self.engine.begin() as conn:
                conn.execute(ins_lineup)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        spider.logger.info(f"Inserted stats for match ID: {match_id}"
        )
        return item


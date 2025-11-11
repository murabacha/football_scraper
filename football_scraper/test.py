from sqlalchemy import MetaData,Column,Table,String,Integer,create_engine,ForeignKey
import pymysql
import json
connect_args = {'ssl':{'mode':'REQUIRED'}}
engine = create_engine('mysql+pymysql://avnadmin:AVNS_TTsiC2_1m5LG1Uh7112@robert-football-database2025-robertthuo2004-f295.i.aivencloud.com:26666/defaultdb',connect_args = connect_args)
metadata = MetaData()
matches = Table('matches', metadata,
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
match_events = Table('match_events', metadata,
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


match_lineups = Table('match_lineups', metadata,
            Column('id', Integer, primary_key=True),
            Column('match_id', Integer, ForeignKey('matches.id')),
            Column('team', String(255)),
            Column('lineup', String(2000)),
            Column('formation', String(50)),
        )

query = match_lineups.select().where(match_lineups.c.match_id == 1)
with engine.connect() as connection:
    result = connection.execute(query)
    test_result = []
    for row in result.fetchall():
        print(row)
        match = {
            'id': row[0],
            'match_id': row[1],
            'team': row[2],
            'lineup': json.dumps(row[3]),
            'formation': row[4],
        }
        test_result.append(match)
    json_data = json.dumps(test_result,indent=4)
    print(json_data)

# query = matches.select().where(matches.c.kickoff == '2025-11-08')
# with engine.connect() as connection:
#     result = connection.execute(query)
#     test_result = []
#     for row in result.fetchall():
#         match = {
#             'id': row[0],
#             'league': row[1],
#             'hometeam': row[2],
#             'awayteam': row[3],
#             'hometeam_goals': row[4],
#             'awayteam_goals': row[5],
#             'kickoff': row[6],
#             'match_url': row[7],
#             'match_completion': row[8],
#         }
#         test_result.append(match)
#     json_data = json.dumps(test_result,indent=4)
#     print(json_data)

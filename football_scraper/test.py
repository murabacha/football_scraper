from sqlalchemy import MetaData,Column,Table,String,Integer,create_engine
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

query = matches.select().where(matches.c.id == 1)
with engine.connect() as connection:
    result = connection.execute(query)
    for row in result:
        print(row)
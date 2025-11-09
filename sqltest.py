from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
import pymysql
engine = create_engine('mysql+pymysql://root:robert@localhost/football')
connection = engine.connect()
matches = Table('matches', MetaData(),
    Column('id', Integer, primary_key=True),
    Column('league', String(255), nullable=False),
    Column('hometeam', String(255)),
    Column('awayteam', String(255)),
    Column('hometeam_goals', Integer),
    Column('awayteam_goals', Integer),
    Column('kickoff', String(255)),
)

day_matches = matches.select().where(matches.c.kickoff == '2025-11-01')
results = connection.execute(day_matches).fetchall()
for row in results:
    data  = {
        "id": row.id,
        "league": row.league,
        "hometeam": row.hometeam,
        "awayteam": row.awayteam,
        "hometeam_goals": row.hometeam_goals,
        "awayteam_goals": row.awayteam_goals,
        "kickoff": row.kickoff,
    }
    import json
    with open('day_matches.json', 'a', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(data)
connection.close()
engine.dispose()
import scrapy
import datetime
import json
import json
from football_scraper.items import FootballScraperItem
import pymysql
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String,Select


class BallScraperSpider(scrapy.Spider):
    def __init__(self):
        self.live_matches = 0
        self.engine = create_engine('mysql+pymysql://robert:robert@localhost/football')
        self.metadata = MetaData()
        self.live_matches = Table('live_matches', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('match_id', String(100), unique=True, nullable=False))
        self.metadata.create_all(self.engine)
        self.connection = self.engine.connect()
        st = Select(self.live_matches)
        result = self.connection.execute(st)
        for row in result:
            print('-----------------------------------')
            print(type(row[-1]),row[-1])
            print('-----------------------------------')
        # Clear the live_matches table at the start of the spider
        self.connection.execute(self.live_matches.delete())
        self.connection.commit()
        self.connection.close()

    name = "ball_scraper2"
    allowed_domains = ["onefootball.com"]
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    start_date = today.strftime("%Y-%m-%d")
    start_urls = [f"https://onefootball.com/en/matches?date={start_date}"]
    current_date_string = start_date
    # Initialize current_date from the configured start string so decrementing works correctly
    current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    def parse(self, response):
        current_url = response.url
        current_now_date = current_url.split('=')[-1]
        self.input_date = datetime.datetime.strptime(current_now_date, "%Y-%m-%d").date()


        json_data = response.css('script#__NEXT_DATA__::text').get()
        data = json.loads(json_data)
        containers = data['props']['pageProps']['containers']
        links = []
        
        for container in containers:
            
            try:
                match_cards  = container['type']['fullWidth']['component']['contentType']['matchCardsList']['matchCards']
                for match in match_cards:
                    link = match.get('link')
                    links.append(link)
               
            except Exception as e:
                self.logger.warning(f"Could not find link in container: {e}")
                continue
       
        for link in links:
            match_url = link
        json_data = response.css('script#__NEXT_DATA__::text').get()
        data = json.loads(json_data)
        containers = data['props']['pageProps']['containers']
        links = []
        
        for container in containers:
            
            try:
                match_cards  = container['type']['fullWidth']['component']['contentType']['matchCardsList']['matchCards']
                for match in match_cards:
                    link = match.get('link')
                    links.append(link)
               
            except Exception as e:
                continue
       
        for link in links:
            match_url = link
            if match_url:
                url = f"https://onefootball.com{match_url}"
                yield response.follow(url, callback=self.parse_stats, priority=10,dont_filter=True)
            else:
                # skip missing links
                continue

       
    def parse_stats(self, response):
        ball_item = FootballScraperItem()
        match_completion =  response.css('div.MatchScore_data__ahxqz span.title-8-medium::text').get() or response.css('div.MatchScore_data__ahxqz span.title-8-medium.MatchScore_highlightedText__hXFt7').get()
        if match_completion == 'Live':
            url = response.url.split('/')[-1]
            with self.engine.connect() as connection:
                insert_stmt = self.live_matches.insert().values(match_id=url)
                connection.execute(insert_stmt)
                connection.commit()
            print('********************************************')
            self.logger.info(f"added live match: {url}")
            print('********************************************')
            return 
   
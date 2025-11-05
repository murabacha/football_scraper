# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FootballScraperItem(scrapy.Item):
    league = scrapy.Field()
    hometeam = scrapy.Field()
    awayteam = scrapy.Field()
    hometeam_goals = scrapy.Field()
    awayteam_goals = scrapy.Field()
    events_hometeam = scrapy.Field()
    events_awayteam = scrapy.Field()
    possession_Home = scrapy.Field()
    Possession_Away = scrapy.Field()
    Total_shots_Home = scrapy.Field()
    Total_shots_Away = scrapy.Field()
    Shots_on_target_Home = scrapy.Field()
    Shots_on_target_Away = scrapy.Field()
    Duels_won_Home = scrapy.Field()
    Duels_won_Away = scrapy.Field()
    kickoff = scrapy.Field()
    stadium = scrapy.Field()

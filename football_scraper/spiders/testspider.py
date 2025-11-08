import scrapy
import json


class TestspiderSpider(scrapy.Spider):
    name = "testspider"
    allowed_domains = ["onefootball.com"]
    start_urls = ["https://onefootball.com/en/match/2642902"]

    def parse(self, response):
        match_time = response.css('div.MatchScore_data__ahxqz span.title-8-medium::text').get()
        print(match_time)
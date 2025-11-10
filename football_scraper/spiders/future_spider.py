import scrapy
import datetime


class FutureSpiderSpider(scrapy.Spider):
    name = "future_spider"
    allowed_domains = ["onefootball.com"]
    today = datetime.date.today() + datetime.timedelta(days=1)
    today_string = today.strftime("%Y-%m-%d")
    start_urls = [f"https://onefootball.com{today_string}"]
    current_date = today

    def parse(self, response):
        next_date = self.today + datetime.timedelta(days=1)
        next_date_str = next_date.strftime("%Y-%m-%d")
        next_url = f"https://onefootball.com/en/matches?date={next_date_str}"
        self.current_date = next_date
        yield scrapy.Request(next_url, callback=self.parse, priority=-10)
        pass

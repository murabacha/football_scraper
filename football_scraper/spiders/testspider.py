import scrapy
import json


class TestspiderSpider(scrapy.Spider):
    name = "testspider"
    allowed_domains = ["onefootball.com"]
    start_urls = ["https://search-api.onefootball.com/v2/en/search?q=laliga"]
    urls = []
    def parse(self, response):
        
        data  = response.json()
        results = data.get('competitions')
        for result in results:
            match_url = result.get('url')
            self.urls.append(match_url)
            with open('leagues.txt', 'a') as f:
                f.write(f'{match_url}\n')
        
        actual_urls = list(set(self.urls))
        print(len(actual_urls))
        print(actual_urls)
            

        with open ('C:\\Users\\PC\\3D Objects\\leagues.txt', 'r') as f:
            for line in f:
                if line == 'league':
                    continue
                else:
                    api_url = 'https://search-api.onefootball.com/v2/en/search?q='
                    # new_line = line.replace(' ','%20')
                  
                    # new_line = new_line.replace('\'','%27')

                    # new_url = api_url+new_line
                    new_url = api_url+line
                    yield response.follow(new_url, callback=self.parse)
        
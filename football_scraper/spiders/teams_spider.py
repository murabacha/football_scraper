import scrapy
from football_scraper.items import TeamItem


class LeagueSpiderSpider(scrapy.Spider):
    name = "teams_spider"
    allowed_domains = ["onefootball.com"]
    start_urls = ["https://onefootball.com/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'football_scraper.pipelines.SaveTeamPipeline': 300,
            
        }
        
    }
    letter = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    
    def start_requests(self):
        for letter in self.letter:
            url = f"https://onefootball.com/en/all-teams/{letter}"
            yield scrapy.Request(url=url, callback=self.parse,cb_kwargs={'letter':letter})
            
    def parse(self, response,letter):
        teams = response.css('ul.DirectoryExpandedList_list__uxegJ li')
        self.logger.info(f"Found {len(teams)} teams on this page")
        for team in teams:
            link = team.css('a.title-7-regular.DirectoryExpandedList_link__Wn8xz::attr(href)').get()
            url = f'https://onefootball.com{link}/squad'
            yield scrapy.Request(url=url, callback=self.parse_team)
            
        number_of_pages = int(response.css('p.title-8-medium.SimplePagination_message__dQGr_::text').get().split(' ')[-1])
        for page in range(2, number_of_pages + 1):
            url = f"https://onefootball.com/en/all-teams/{letter}?page={page}"
            yield scrapy.Request(url=url, callback=self.parse,cb_kwargs={'letter':letter})
            
    def parse_team(self, response):
        team_item = TeamItem()
        team = response.css('p.title-1-bold-druk.EntityTitle_title__sWSgU::text').get()
        team_logo = response.css('div.EntityTitle_content__q7h3j img ::attr(src)').get()
        positions = response.css('article.EntityNavigationGrid_container__yobpK')
        team_players = {}
        for position in positions:
            position_name = position.css('header.EntityNavigationGrid_title__uYeO0.title-7-bold::text').get()
            players = position.css('ul.EntityNavigationGrid_list__zMWNw li')
            position_players = []
            for player in players:
                player_name = player.css('p.EntityNavigationLink_title__zbfTk.title-7-bold::text').get()
                player_image = player.css('div.EntityNavigationLink_content__kytlW img ::attr(src)').get()
                player_details = {
                    'name': player_name,
                    'image': player_image,
                }
                position_players.append(player_details)
            team_players[position_name] = position_players

        team_item['team_name'] = team
        team_item['team_logo'] = team_logo
        team_item['squad'] = team_players
        yield team_item
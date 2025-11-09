import scrapy
import datetime
import json
from football_scraper.items import FootballScraperItem


class BallScraperSpider(scrapy.Spider):
    name = "ball_scraper"
    allowed_domains = ["onefootball.com"]
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_string = yesterday.strftime("%Y-%m-%d")
    start_urls = [f"https://onefootball.com/en/matches?date={yesterday_string}"]
    current_date_string = yesterday_string
    # Initialize current_date from the configured start string so decrementing works correctly
    current_date = datetime.datetime.strptime(yesterday_string, "%Y-%m-%d").date()
    def parse(self, response):
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
        print('******************************************************************************************************************************')
        print(len(links))
        print(links)
        print('******************************************************************************************************************************')
        # Schedule per-match requests with higher priority so they are
        # processed before the next-date listing request. This reduces the
        # chance Scrapy will fetch the next date while some match pages
        # are still pending.
        for link in links:
            match_url = link
            if match_url:
                url = f"https://onefootball.com{match_url}"
                yield response.follow(url, callback=self.parse_stats, priority=10)
            else:
                # skip missing links
                continue

        # Handle date change after scheduling match pages. Use a low priority
        # for the next-date request so it is processed after match pages.
        next_date = self.current_date - datetime.timedelta(days=1)
        next_date_str = next_date.strftime("%Y-%m-%d")
        self.current_date_string = next_date_str
        next_url = f"https://onefootball.com/en/matches?date={next_date_str}"
        self.current_date = next_date
        yield scrapy.Request(next_url, callback=self.parse, priority=-10)

    def parse_stats(self, response):
        # Create a new item instance for each match
        ball_item = FootballScraperItem()
        match_completion =  response.css('div.MatchScore_data__ahxqz span.title-8-medium::text').get() or response.css('div.MatchScore_data__ahxqz span.title-8-medium.MatchScore_highlightedText__hXFt7').get()
        ball_item['match_completion'] = match_completion    
        json_data = response.css('script#__NEXT_DATA__::text').get()
        data = json.loads(json_data)
        match_info = data['props']['pageProps']['containers']
        ball_item['events'] = []
        for match in match_info:
            try:
                match_events = match['type']['fullWidth']['component']['contentType']['matchEvents']['events']
                for event in match_events:
                    time = event.get('timeline', None)
                    the_event = event.get('type', None)
                    event_name = event.get('name',None)
                    team_side = event.get('teamSide', None)
                    if team_side == 0:
                        team = 'hometeam'
                    elif team_side == 1:
                        team = 'awayteam'
                    if event_name == 'Goal':
                        scorer = the_event['goal'].get('scorer', None).get('name', None)
                        assist = the_event['goal'].get('assistant', None).get('name', None)
                        event_info = {
                            "team": team,
                            "minute": time,
                            "type": event_name,
                            "player_in": None,
                            "player_out": None,
                            'player': None,
                            'scorer': scorer,
                            'assist': assist

                        }
                    elif event_name == 'Yellow card':
                        player = the_event['card'].get('player', None).get('name', None)
                        event_info = {
                            "team": team,
                            "minute": time,
                            "type": event_name,
                            "player_in": None,
                            "player_out": None,
                            'player': player,
                            'scorer': None,
                            'assist': None

                        }
                    elif event_name == 'Substitution':
                        player_in = the_event['substitution'].get('playerIn', None).get('name', None)
                        player_out = the_event['substitution'].get('playerOut', None).get('name', None)
                        event_info = {
                            "team": team,
                            "minute": time,
                            "type": event_name,
                            "player_in": player_in,
                            "player_out": player_out,
                            'player': None,
                            'scorer': None,
                            'assist': None

                        }
                    elif event_name == 'Red card':
                        player = the_event['card'].get('player', None).get('name', None)
                        event_info = {
                            "team": team,
                            "minute": time,
                            "type": event_name,
                            "player_in": None,
                            "player_out": None,
                            'player': player,
                            'scorer': None,
                            'assist': None

                        }
                    elif event_name =='Own goal':
                        scorer = the_event['goal'].get('scorer', None).get('name', None)
                        event_info = {
                            "team": team,
                            "minute": time,
                            "type": event_name,
                            "player_in": None,
                            "player_out": None,
                            'player': None,
                            'scorer': scorer,
                            'assist': None

                        }
                    ball_item['events'].append(event_info) #append event_info
                               
            except Exception as e:
                continue
       
    
        
        ball_item['match_url'] = response.url
        ball_item['league'] = response.css('span.title-7-medium.MatchScoreCompetition_competitionName__wONrf::text').get()
        teams = response.css('span.MatchScoreTeam_name__zzQrD.MatchScoreTeam_titleStyle__V_kbV::text').getall()
        ball_item['hometeam'] = teams[0].strip() if len(teams) > 0 else None
        ball_item['awayteam'] = teams[1].strip() if len(teams) > 1 else None
        goals_scored = response.css('p.MatchScore_scores__Hnn5f.title-2-bold-druk span::text').getall()
        ball_item['hometeam_goals'] = goals_scored[0].strip() if len(goals_scored) > 0 else None
        ball_item['awayteam_goals'] = goals_scored[2].strip() if len(goals_scored) > 2 else None
        
        
        match_statistics = response.css('li.MatchStatsEntry_container__bI_WW')
        for stat in match_statistics:
                stat_name = stat.css('p.title-8-regular.MatchStatsEntry_title__Vvz4Y::text').get()
                hometeam_value = stat.css('p.title-7-medium.MatchStatsEntry_homeValue__1MQNU::text').getall()
                homevalue = hometeam_value[0].strip()+" "+hometeam_value[1].strip() if len(hometeam_value) > 1 else hometeam_value[0].strip()
                awayteam_value = stat.css('p.title-7-medium.MatchStatsEntry_awayValue__rgzMD::text').getall()
                awayvalue = awayteam_value[0].strip()+" "+awayteam_value[1].strip() if len(awayteam_value) > 1 else awayteam_value[0].strip()
                if stat_name == "Possession":
                    ball_item['possession_Home'] = homevalue
                    ball_item['Possession_Away'] = awayvalue
                elif stat_name == "Total shots":
                    ball_item['Total_shots_Home'] = homevalue
                    ball_item['Total_shots_Away'] = awayvalue
                elif stat_name == "Shots on target":
                    ball_item['Shots_on_target_Home'] = homevalue
                    ball_item['Shots_on_target_Away'] = awayvalue
                elif stat_name == "Duels won":
                    ball_item['Duels_won_Home'] = homevalue
                    ball_item['Duels_won_Away'] = awayvalue
        extra_info = response.css('span.title-8-regular.MatchInfoEntry_subtitle__Mb7Jd::text').getall()
        ball_item['kickoff'] = self.current_date_string
        ball_item["stadium"] = extra_info[2] if len(extra_info) > 2 else None

        second_json_data = response.css('script#__NEXT_DATA__::text').get()
        data = json.loads(second_json_data)
        match_info = data['props']['pageProps']['containers']
        ball_item['match_lineup'] = []
        for match in match_info:
            try:
                lineup_container = match['type']['grid']['items']
                temporary_list = lineup_container[0]
                second_temporary_list = temporary_list['components'][0]
                hometeam_lineup = second_temporary_list['contentType']['matchLineup']['variant']['lineup']['homeTeam']
                awayteam_lineup = second_temporary_list['contentType']['matchLineup']['variant']['lineup']['awayTeam']
                hometeam = hometeam_lineup.get('teamName')
                awayteam = awayteam_lineup.get('teamName')

                if hometeam_lineup:
                    if hometeam_lineup['variant'].get('formation') is not None:
                        line_up = hometeam_lineup['variant']['formation'].get('rows')
                   
                        hometeam_formation = ''
                        the_home_lineup = []
                        for row in line_up:
                            players = row['players']
                            hometeam_formation += str(len(players)) + '-'
                            for player in players:
                                player_name = player.get('name')

                                jersey_number = player.get('jerseyNumber')
                                player_info = {
                                    'player_name': player_name,
                                    'jersey_number': jersey_number
                                }
                                the_home_lineup.append(player_info)
                        ball_item['match_lineup'].append({
                            'team': hometeam,
                            'lineup': the_home_lineup,
                            'home_formation': hometeam_formation
                        })
                    else:
                        line_up = hometeam_lineup['variant'].get('flat').get('players', [])
                        hometeam_formation = ''
                        the_home_lineup = []
                        for player in line_up:
                            player_name = player.get('name')
                            jersey_number = player.get('jerseyNumber')
                            player_info = {
                                'player_name': player_name,
                                'jersey_number': jersey_number
                            }
                            the_home_lineup.append(player_info)
                        if len(hometeam_formation) == 0:
                            hometeam_formation = 'N/A'
                        ball_item['match_lineup'].append({
                            'team': hometeam,
                            'lineup': the_home_lineup,
                            'home_formation': hometeam_formation
                        })

                if awayteam_lineup:
                    if awayteam_lineup['variant'].get('formation') is not None:
                        line_up = awayteam_lineup['variant']['formation'].get('rows')
                        awayteam_formation = ''
                        the_away_lineup = []
                        for row in line_up:
                            players = row['players']
                            awayteam_formation += str(len(players)) + '-'
                            for player in players:
                                player_name = player.get('name')
                                jersey_number = player.get('jerseyNumber')
                                player_info = {
                                    'player_name': player_name,
                                    'jersey_number': jersey_number
                                }
                                the_away_lineup.append(player_info)
                        ball_item['match_lineup'].append({
                            'team': awayteam,
                            'lineup': the_away_lineup,
                            'away_formation': awayteam_formation
                        })
                    else:
                        line_up = awayteam_lineup['variant'].get('flat').get('players', [])
                        hometeam_formation = ''
                        the_home_lineup = []
                        for player in line_up:
                            player_name = player.get('name')
                            jersey_number = player.get('jerseyNumber')
                            player_info = {
                                'player_name': player_name,
                                'jersey_number': jersey_number
                            }
                            the_home_lineup.append(player_info)
                        if len(hometeam_formation) == 0:
                            hometeam_formation = 'N/A'
                        ball_item['match_lineup'].append({
                            'team': hometeam,
                            'lineup': the_home_lineup,
                            'home_formation': hometeam_formation
                        })
            except Exception as e:
                self.logger.warning(f"Could not find lineup in match: {e}")
                continue
            # print('========================================')
            # print(hometeam_formation)
            # print(awayteam_formation)
            # print('========================================')
        


        yield ball_item


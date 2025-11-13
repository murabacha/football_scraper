import scrapy
import datetime
import json
import json
from football_scraper.items import FootballScraperItem


class BallScraperSpider(scrapy.Spider):
    name = "ball_scraper2"
    allowed_domains = ["onefootball.com"]
    # today = datetime.date.today()
    # yesterday = today - datetime.timedelta(days=1)
    start_date = '2025-07-20'#yesterday.strftime("%Y-%m-%d")
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
                yield response.follow(url, callback=self.parse_stats, priority=10,dont_filter=True)
            else:
                # skip missing links
                continue

        # Handle date change after scheduling match pages and  Using a low priority for the next-date request so it is processed after match pages.
        next_date = self.current_date - datetime.timedelta(days=1)
        next_date_str = next_date.strftime("%Y-%m-%d")
        self.current_date_string = next_date_str
        self.current_date_string = next_date_str
        next_url = f"https://onefootball.com/en/matches?date={next_date_str}"
        self.current_date = next_date
        yield scrapy.Request(next_url, callback=self.parse, priority=-10)

    def parse_stats(self, response):
        # Create a new item instance for each match
        referrer = response.request.headers.get('Referer')
        if referrer:
            referrer = referrer.decode('utf-8')
        the_date = referrer.split('=')[-1]
        the_date_date = datetime.datetime.strptime(the_date, "%Y-%m-%d").date()
        ball_item = FootballScraperItem()
        match_completion =  response.css('div.MatchScore_data__ahxqz span.title-8-medium::text').get() or response.css('div.MatchScore_data__ahxqz span.title-8-medium.MatchScore_highlightedText__hXFt7').get()
        if match_completion is None:
            match_time = response.css('div.MatchScore_data__ahxqz span.title-6-bold.MatchScore_numeric__ke8YT::text').get()
            ball_item['match_time'] = match_time
            game_time = response.css('div.MatchScore_data__ahxqz span.title-8-medium.MatchScore_highlightedText__hXFt7::text').get()
            ball_item['game_time'] = game_time
            ball_item['league'] = response.css('span.title-7-medium.MatchScoreCompetition_competitionName__wONrf::text').get()
            ball_item['hometeam'] = response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_home__9Ehdk.MatchScoreTeam_preMatch__BYiz7 span.MatchScoreTeam_name__zzQrD::text').get()
            ball_item['awayteam'] = response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_away__O_HfB.MatchScoreTeam_preMatch__BYiz7 span.MatchScoreTeam_name__zzQrD::text').get()
            home_full_url = response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_home__9Ehdk.MatchScoreTeam_preMatch__BYiz7 span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get()\
            or  response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_home__9Ehdk span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get() 
            if home_full_url:
                actual_url = home_full_url.split(' 1x')[0]
                ball_item['hometeam_logo'] = actual_url
            away_full_url = response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_away__O_HfB.MatchScoreTeam_preMatch__BYiz7 span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get()\
            or response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_away__O_HfB span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get()
            if away_full_url:
                actual_url = away_full_url.split(' 1x')[0]
                ball_item['awayteam_logo'] = actual_url
            ball_item['match_url'] = response.url
            ball_item['match_completion'] = 'pending'
            ball_item['hometeam_goals'] = '0'
            ball_item['awayteam_goals'] = '0'
            ball_item['kickoff'] = the_date_date  #-datetime.timedelta(days=1)
            ball_item['events'] = []
            ball_item['stadium'] = response.css('li div.MatchInfo_entry__94sgy span.title-8-regular.MatchInfoEntry_subtitle__Mb7Jd::text').getall()[-1]
            ball_item['match_lineup'] = []
            ball_item['possession_Home'] = None
            ball_item['Possession_Away'] = None
            ball_item['Total_shots_Home'] = None
            ball_item['Total_shots_Away'] = None
            ball_item['Shots_on_target_Home'] = None
            ball_item['Shots_on_target_Away'] = None
            ball_item['Duels_won_Home'] = None
            ball_item['Duels_won_Away'] = None
        else:
            match_time = response.css('div.MatchScore_data__ahxqz span.title-6-bold.MatchScore_numeric__ke8YT::text').get()
            ball_item['match_time'] = match_time
            game_time = response.css('span.title-8-medium.MatchScore_highlightedText__hXFt7::text').get()
            ball_item['game_time'] = game_time
        

            ball_item['match_completion'] = match_completion    
            json_data = response.css('script#__NEXT_DATA__::text').get()
            data = json.loads(json_data)
            match_info = data['props']['pageProps']['containers']
            ball_item['events'] = []
            match_events = None
            for match in match_info:
                try:
                    match_events = match['type']['fullWidth']['component']['contentType']['matchEvents']['events']
                except Exception as e:
                    continue
            if match_events:
                for event in match_events:
                    try:
                        time = event.get('timeline', None)
                        the_event = event.get('type', None)
                        event_name = event.get('name',None)
                        team_side = event.get('teamSide', None)
                        if team_side == 0:
                            team = 'hometeam'
                        elif team_side == 1:
                            team = 'awayteam'
                        if event_name == 'Penalty':
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
                        if event_name == 'Goal':
                            scorer = the_event['goal'].get('scorer', None).get('name', None)
                            try:
                                assist = the_event['goal'].get('assistant', None).get('name', None)
                            except Exception as e:
                                assist = None
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
        
            home_full_url = response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_home__9Ehdk.MatchScoreTeam_preMatch__BYiz7 span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get()\
            or  response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_home__9Ehdk span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get() 
            if home_full_url:
                actual_url = home_full_url.split(' 1x')[0]
                ball_item['hometeam_logo'] = actual_url
            away_full_url = response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_away__O_HfB.MatchScoreTeam_preMatch__BYiz7 span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get()\
            or response.css('a.MatchScoreTeam_container__1X5t5.MatchScoreTeam_away__O_HfB span.EntityLogo_entityLogo__29IUu.EntityLogo_entityLogoWithHover__XynBQ.MatchScoreTeam_icon__XiDSl img::attr(srcset)').get()
            if away_full_url:
                actual_url = away_full_url.split(' 1x')[0]
                ball_item['awayteam_logo'] = actual_url
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
                ball_item['hometeam_goals'] = goals_scored[0].strip() if len(goals_scored) > 0 else None
                ball_item['awayteam_goals'] = goals_scored[2].strip() if len(goals_scored) > 2 else None
            
            
            match_statistics = response.css('li.MatchStatsEntry_container__bI_WW')
            if match_statistics:
                
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
            else:
                ball_item['possession_Home'] = None
                ball_item['Possession_Away'] = None
                ball_item['Total_shots_Home'] = None
                ball_item['Total_shots_Away'] = None
                ball_item['Shots_on_target_Home'] = None
                ball_item['Shots_on_target_Away'] = None
                ball_item['Duels_won_Home'] = None
                ball_item['Duels_won_Away'] = None
            extra_info = response.css('span.title-8-regular.MatchInfoEntry_subtitle__Mb7Jd::text').getall()
            ball_item["stadium"] = extra_info[2] if len(extra_info) > 2 else None
            ball_item['kickoff'] = the_date_date

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
                                'lineup': the_home_lineup if len(the_home_lineup) > 0 else None,
                                'home_formation': hometeam_formation if len(hometeam_formation) > 0 else None
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
                            ball_item['match_lineup'].append({
                                'team': hometeam,
                                'lineup': the_home_lineup if len(the_home_lineup) > 0 else None,
                                'home_formation': hometeam_formation if len(hometeam_formation) > 0 else None
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
                                'lineup': the_away_lineup if len(the_away_lineup) > 0 else None,
                                'away_formation': awayteam_formation if len(awayteam_formation) > 0 else None
                            })
                        else:
                            line_up = awayteam_lineup['variant'].get('flat').get('players', [])
                            awayteam_formation = ''
                            the_away_lineup = []
                            for player in line_up:
                                player_name = player.get('name')
                                jersey_number = player.get('jerseyNumber')
                                player_info = {
                                    'player_name': player_name,
                                    'jersey_number': jersey_number
                                }
                                the_home_lineup.append(player_info)
                            ball_item['match_lineup'].append({
                                'team': awayteam,
                                'lineup': the_away_lineup if len(the_away_lineup) > 0 else None,
                                'away_formation': awayteam_formation if len(awayteam_formation) > 0 else None
                            })
                except Exception as e:
                    self.logger.warning(f"Could not find lineup in match: {e}")
                    continue
            


        yield ball_item



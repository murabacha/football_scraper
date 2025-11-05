import scrapy
import datetime
from football_scraper.items import FootballScraperItem


class BallScraperSpider(scrapy.Spider):
    name = "ball_scraper"
    allowed_domains = ["onefootball.com"]
    start_urls = ["https://onefootball.com/en/matches?date=2025-11-02"]
    current_date = datetime.datetime.strptime("2025-11-02", "%Y-%m-%d").date()
    ball_item = FootballScraperItem()
    def parse(self, response):
        matches = response.css('a.MatchCard_matchCard__iOv4G')
        for match in matches:
            match_url = match.css('a.MatchCard_matchCard__iOv4G::attr(href)').get()
                # teams = match.css('span.SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D::text').getall()
                # scores = match.css('span.SimpleMatchCardTeam_simpleMatchCardTeam__score__UYMc_::text').getall()
                # stats_url = match.css('a.MatchCard_matchCard__iOv4G::attr(href)').get()
                # hometeam = teams[0].strip() if len(teams) > 0 else None
                # awayteam = teams[1].strip() if len(teams) > 1 else None
                # homescore = scores[0].strip() if len(scores) > 0 else None
                # awayscore = scores[1].strip() if len(scores) > 1 else None
                # data =  {
                #     "league": league_name,
                #     "hometeam": hometeam,
                #     "awayteam": awayteam,
                #     "hometeam_goals": homescore,
                #     "awayteam_goals": awayscore,
                # }
            if match_url:
                url = f"https://onefootball.com{match_url}"
                yield response.follow(url, callback=self.parse_stats)
            else:
                yield self.ball_item
        
        # Handle date change after processing all matches
        next_date = self.current_date - datetime.timedelta(days=1)
        next_date_str = next_date.strftime("%Y-%m-%d")
        next_url = f"https://onefootball.com/en/matches?date={next_date_str}"
        self.current_date = next_date
        yield response.follow(next_url, callback=self.parse)

    def parse_stats(self, response):
        
        hometeam_events = response.css('li.MatchEvents_matchEventsItem__Zvim8.MatchEvents_matchEventsItemHome__Epaxa')
        awayteamevents = response.css('li.MatchEvents_matchEventsItem__Zvim8.MatchEvents_matchEventsItemAway__vwWOY')
        self.ball_item['league'] = response.css('span.title-7-medium.MatchScoreCompetition_competitionName__wONrf::text').get()
        teams = response.css('span.MatchScoreTeam_name__zzQrD.MatchScoreTeam_titleStyle__V_kbV::text').getall()
        self.ball_item['hometeam'] = teams[0].strip() if len(teams) > 0 else self.ball_item['hometeam']
        self.ball_item['awayteam'] = teams[1].strip() if len(teams) > 1 else self.ball_item['awayteam']
        goals_scored = response.css('p.MatchScore_scores__Hnn5f.title-2-bold-druk span::text').getall()
        self.ball_item['hometeam_goals'] = goals_scored[0].strip() if len(goals_scored) > 0 else self.ball_item['hometeam_goals']
        self.ball_item['awayteam_goals'] = goals_scored[2].strip() if len(goals_scored) > 2 else self.ball_item['awayteam_goals']
        self.ball_item['events_hometeam'] = []
        self.ball_item['events_awayteam'] = []
        for event in hometeam_events:
            event_minute = event.css('p.title-8-bold.MatchEventsTimeline_matchEventsItemTimeline__vWqLt.MatchEventsTimeline_matchEventsItemTimelineOuter__IcZ2Z::text').get()
            icon_url = event.css('picture.ImageWithSets_of-image__picture__4hzsN source::attr(srcset)').get()
            event_type = None
            if 'own' in icon_url:
                event_type = "own_goal"
            elif 'goal' in icon_url:
                event_type = "goal"
            elif 'yellow-card' in icon_url:
                event_type = "yellow_card"
            elif 'red-card' in icon_url:
                event_type = "red_card"
            elif 'substitution' in icon_url:
                event_type = "substitution"
            elif 'penalty' in icon_url:
                event_type = "penalty"
            if event_type == "substitution":
                player_in = event.css('p.title-8-medium::text').get()
                player_out = event.css('p.title-8-regular.MatchEventCard_matchEventsSecondaryText__rjQsQ::text').get()
                event_info = {
                    #"team": "hometeam",
                    "minute": event_minute,
                    "type": event_type,
                    "player_in": player_in,
                    "player_out": player_out
                }
                
                self.ball_item['events_hometeam'] .append(event_info) #append event_info
            elif event_type == "goal":
                scorer = event.css('p.title-8-medium::text').get()
                assist = event.css('p.title-8-regular.MatchEventCard_matchEventsSecondaryText__rjQsQ::text').get()
                event_info = {
                    #"team": "hometeam",
                    "minute": event_minute,
                    "type": event_type,
                    "scorer": scorer,
                    "assist": assist if assist != 'Goal' else "no assist"
                }
                self.ball_item['events_hometeam'] .append(event_info) #append event_info
            else:
                player_involved = event.css('p.title-8-medium::text').get()
                event_info = {
                    #"team": "hometeam",
                    "minute": event_minute,
                    "type": event_type,
                    "player": player_involved
                }
                self.ball_item['events_hometeam'] .append(event_info) #append event_info
        for event in awayteamevents:
            event_minute = event.css('p.title-8-bold.MatchEventsTimeline_matchEventsItemTimeline__vWqLt.MatchEventsTimeline_matchEventsItemTimelineOuter__IcZ2Z::text').get()
            icon_url = event.css('picture.ImageWithSets_of-image__picture__4hzsN source::attr(srcset)').get()
            event_type = None
            if 'own' in icon_url:
                event_type = "own_goal"
            elif 'goal' in icon_url:
                event_type = "goal"
            elif 'yellow-card' in icon_url:
                event_type = "yellow_card"
            elif 'red-card' in icon_url:
                event_type = "red_card"
            elif 'substitution' in icon_url:
                event_type = "substitution"
            elif 'penalty' in icon_url:
                event_type = "penalty"
            if event_type == "substitution":
                player_in = event.css('p.title-8-medium::text').get()
                player_out = event.css('p.title-8-regular.MatchEventCard_matchEventsSecondaryText__rjQsQ::text').get()
                event_info = {
                    #"team": "awayteam",
                    "minute": event_minute,
                    "type": event_type,
                    "player_in": player_in,
                    "player_out": player_out
                }
                self.ball_item['events_awayteam'] .append(event_info) #append event_info
            elif event_type == "goal":
                scorer = event.css('p.title-8-medium::text').get()
                assist = event.css('p.title-8-regular.MatchEventCard_matchEventsSecondaryText__rjQsQ::text').get()
                event_info = {
                    #"team": "awayteam",
                    "minute": event_minute,
                    "type": event_type,
                    "scorer": scorer,
                    "assist": assist if assist != 'Goal' else "no assist"
                }
                self.ball_item['events_awayteam'] .append(event_info) #append event_info
            else:
                player_involved = event.css('p.title-8-medium::text').get()
                event_info = {
                    #"team": "awayteam",
                    "minute": event_minute,
                    "type": event_type,
                    "player": player_involved
                }
                self.ball_item['events_awayteam'] .append(event_info) #append event_info
            match_statistics = response.css('li.MatchStatsEntry_container__bI_WW')
            for stat in match_statistics:
                stat_name = stat.css('p.title-8-regular.MatchStatsEntry_title__Vvz4Y::text').get()
                hometeam_value = stat.css('p.title-7-medium.MatchStatsEntry_homeValue__1MQNU::text').getall()
                homevalue = hometeam_value[0].strip()+" "+hometeam_value[1].strip() if len(hometeam_value) > 1 else hometeam_value[0].strip()
                awayteam_value = stat.css('p.title-7-medium.MatchStatsEntry_awayValue__rgzMD::text').getall()
                awayvalue = awayteam_value[0].strip()+" "+awayteam_value[1].strip() if len(awayteam_value) > 1 else awayteam_value[0].strip()
                if stat_name == "Possession":
                    self.ball_item['possession_Home'] = homevalue
                    self.ball_item['Possession_Away'] = awayvalue
                elif stat_name == "Total shots":
                    self.ball_item['Total_shots_Home'] = homevalue
                    self.ball_item['Total_shots_Away'] = awayvalue
                elif stat_name == "Shots on target":
                    self.ball_item['Shots_on_target_Home'] = homevalue
                    self.ball_item['Shots_on_target_Away'] = awayvalue
                elif stat_name == "Duels won":
                    self.ball_item['Duels_won_Home'] = homevalue
                    self.ball_item['Duels_won_Away'] = awayvalue
            extra_info = response.css('span.title-8-regular.MatchInfoEntry_subtitle__Mb7Jd::text').getall()
            self.ball_item['kickoff'] = extra_info[1]
            self.ball_item["stadium"] = extra_info[2]


        yield self.ball_item


import scrapy
import datetime


class BallScraperSpider(scrapy.Spider):
    name = "ball_scraper"
    allowed_domains = ["onefootball.com"]
    start_urls = ["https://onefootball.com/en/matches?date=2025-11-02"]
    current_date = datetime.datetime.strptime("2025-11-02", "%Y-%m-%d").date()

    def parse(self, response):
        leagues = response.css("div.XpaLayout_xpaLayoutContainerComponentResolver__jwpy6.xpaLayoutContainerComponentResolver--matchCardsList")
        for league in leagues:
            league_name = league.css('h2.title-6-bold.Title_leftAlign__mYh6r::text').get()
            matches = league.css("a.MatchCard_matchCard__iOv4G")
            for match in matches:
                teams = match.css('span.SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D::text').getall()
                scores = match.css('span.SimpleMatchCardTeam_simpleMatchCardTeam__score__UYMc_::text').getall()
                stats_url = match.css('a.MatchCard_matchCard__iOv4G::attr(href)').get()
                hometeam = teams[0].strip() if len(teams) > 0 else None
                awayteam = teams[1].strip() if len(teams) > 1 else None
                homescore = scores[0].strip() if len(scores) > 0 else None
                awayscore = scores[1].strip() if len(scores) > 1 else None
                data =  {
                    "league": league_name,
                    "hometeam": hometeam,
                    "awayteam": awayteam,
                    f"{hometeam} goals": homescore,
                    f"{awayteam} goals": awayscore,
                }
                if stats_url:
                    url = f"https://onefootball.com{stats_url}"
                    yield response.follow(url, callback=self.parse_stats,meta={'stats':data})
                else:
                    yield data
        
        # Handle date change after processing all matches
        next_date = self.current_date - datetime.timedelta(days=1)
        next_date_str = next_date.strftime("%Y-%m-%d")
        next_url = f"https://onefootball.com/en/matches?date={next_date_str}"
        self.current_date = next_date
        yield response.follow(next_url, callback=self.parse)

    def parse_stats(self, response):
        stats_data = response.meta['stats']
        stats_data["events"] = []
        hometeam_events = response.css('li.MatchEvents_matchEventsItem__Zvim8.MatchEvents_matchEventsItemHome__Epaxa')
        awayteamevents = response.css('li.MatchEvents_matchEventsItem__Zvim8.MatchEvents_matchEventsItemAway__vwWOY')
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
                    "team": stats_data["hometeam"],
                    "minute": event_minute,
                    "type": event_type,
                    "player_in": player_in,
                    "player_out": player_out
                }
                stats_data["events"] .append(event_info) #append event_info
            elif event_type == "goal":
                scorer = event.css('p.title-8-medium::text').get()
                assist = event.css('p.title-8-regular.MatchEventCard_matchEventsSecondaryText__rjQsQ::text').get()
                event_info = {
                    "team": stats_data["hometeam"],
                    "minute": event_minute,
                    "type": event_type,
                    "scorer": scorer,
                    "assist": assist if assist != 'Goal' else "no assist"
                }
                stats_data["events"].append(event_info)
            else:
                player_involved = event.css('p.title-8-medium::text').get()
                event_info = {
                    "team": stats_data["hometeam"],
                    "minute": event_minute,
                    "type": event_type,
                    "player": player_involved
                }
                stats_data["events"] .append(event_info) #append event_info
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
                    "team": stats_data["awayteam"],
                    "minute": event_minute,
                    "type": event_type,
                    "player_in": player_in,
                    "player_out": player_out
                }
                stats_data["events"] .append(event_info) #append event_info
            elif event_type == "goal":
                scorer = event.css('p.title-8-medium::text').get()
                assist = event.css('p.title-8-regular.MatchEventCard_matchEventsSecondaryText__rjQsQ::text').get()
                event_info = {
                    "team": stats_data["awayteam"],
                    "minute": event_minute,
                    "type": event_type,
                    "scorer": scorer,
                    "assist": assist if assist != 'Goal' else "no assist"
                }
                stats_data["events"].append(event_info)
            else:
                player_involved = event.css('p.title-8-medium::text').get()
                event_info = {
                    "team": stats_data["awayteam"],
                    "minute": event_minute,
                    "type": event_type,
                    "player": player_involved
                }
                stats_data["events"].append(event_info)
            match_statistics = response.css('li.MatchStatsEntry_container__bI_WW')
            for stat in match_statistics:
                stat_name = stat.css('p.title-8-regular.MatchStatsEntry_title__Vvz4Y::text').get()
                hometeam_value = stat.css('p.title-7-medium.MatchStatsEntry_homeValue__1MQNU::text').getall()
                homevalue = hometeam_value[0].strip()+" "+hometeam_value[1].strip() if len(hometeam_value) > 1 else hometeam_value[0].strip()
                awayteam_value = stat.css('p.title-7-medium.MatchStatsEntry_awayValue__rgzMD::text').getall()
                awayvalue = awayteam_value[0].strip()+" "+awayteam_value[1].strip() if len(awayteam_value) > 1 else awayteam_value[0].strip()
                stats_data[stat_name] = {
                    f"{stats_data['hometeam']}": homevalue,
                    f"{stats_data['awayteam']}": awayvalue
                }
            extra_info = response.css('span.title-8-regular.MatchInfoEntry_subtitle__Mb7Jd::text').getall()
            stats_data["kickoff"] = extra_info[1]
            stats_data["stadium"] = extra_info[2]


        yield stats_data


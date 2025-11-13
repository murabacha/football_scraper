import scrapy
from football_scraper.items import TableItem

class LeagueSpiderSpider(scrapy.Spider):
    name = "league_table_spider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'football_scraper.pipelines.SaveLeagueTablePipeline': 300,
            
        }
        
    }
    allowed_domains = ["onefootball.com"]
    start_urls = ["https://onefootball.com/"]
    leages_urls = ['/en/competition/conmebol-libertadores-femenina-2775', '/en/competition/pro-league-58', '/en/competition/1-divisjon-2985', '/en/competition/a-league-women-2806', '/en/competition/usl-league-one-2915',
                   '/en/competition/socca-champions-league-2986', '/en/competition/campeonato-uruguayo-primera-clausura-81', '/en/competition/baller-league-uk-2988', '/en/competition/efl-league-two-43', '/en/competition/knvb-beker-105', 
                   '/en/competition/superettan-relegation-play-offs-2911', '/en/competition/hrvatski-kup-2852', '/en/competition/scottish-championship-98', '/en/competition/la-liga-2-28', '/en/competition/sueper-lig-8',
                   '/en/competition/chinese-super-league-112', '/en/competition/j2-league-141', '/en/competition/chance-liga-159', '/en/competition/dbu-pokalen-182', '/en/competition/thai-league-cup-2921', 
                   '/en/competition/meistriliiga-2747', '/en/competition/fai-mens-senior-cup-2784', '/en/competition/liga-nacional-de-guatemala-2725', '/en/competition/qatar-stars-league-158', '/en/competition/primera-nacional-164',
                   '/en/competition/mls-next-pro-2919', '/en/competition/tuerkiye-kupasi-78', '/en/competition/kings-league-brazil-2962', '/en/competition/qatari-stars-cup-2927', '/en/competition/womens-super-league-2696',
                   '/en/competition/cypriot-super-cup-2856', '/en/competition/2-frauen-bundesliga-2896', '/en/competition/liga-fpd-2716', '/en/competition/egypt-cup-2917', '/en/competition/torneo-federal-a-2787', '/en/competition/j1-league-38',
                   '/en/competition/fa-cup-17', '/en/competition/scottish-league-one-99', '/en/competition/goiano-197', '/en/competition/2-bundesliga-2', '/en/competition/fifa-u17-womens-world-cup-2951', '/en/competition/ekstraklasa-59', 
                   '/en/competition/persha-liha-2888', '/en/competition/eredivisie-women-2814', '/en/competition/super-league-greece-56', '/en/competition/botola-186', '/en/competition/nike-liga-2723', '/en/competition/puchar-polski-106',
                   '/en/competition/korean-fa-cup-131', '/en/competition/cypriot-cup-2855', '/en/competition/vbet-premier-league-relegation-playoffs-2972', '/en/competition/beker-van-belgiea-117', '/en/competition/cymru-league-cup-2982',
                   '/en/competition/copa-argentina-193', '/en/competition/i-liga-132', '/en/competition/primera-b-206', '/en/competition/kings-cup-2811', '/en/competition/ligue-1-23', '/en/competition/copa-del-rey-18',
                   '/en/competition/copa-gaucha-1892', '/en/competition/k-league-2-2736', '/en/competition/regionalliga-suedwest-51', '/en/competition/iraq-stars-league-2759', '/en/competition/uefa-europa-league-7', 
                   '/en/competition/2-lig-2846', '/en/competition/championnat-national-2-1722', '/en/competition/conmebol-sudamericana-102', '/en/competition/swiss-womens-super-league-2818', '/en/competition/super-liga-2799',
                   '/en/competition/primera-b-metropolitana-165', '/en/competition/slovenian-cup-2885', '/en/competition/fizz-liga-2749', '/en/competition/swpl-1-2913', '/en/competition/primera-division-clausura-175', 
                   '/en/competition/football-national-league-2-1725', '/en/competition/efl-championship-27', '/en/competition/primera-division-apertura-174', '/en/competition/cupa-romaniei-107', '/en/competition/liga-bbva-mx-89', 
                   '/en/competition/chance-narodni-liga-2858', '/en/competition/liga-mx-femenil-2733', '/en/competition/kings-league-italy-2961', '/en/competition/national-league-97', '/en/competition/copa-do-brasil-u20-1898',
                   '/en/competition/dfb-pokal-frauen-2743', '/en/competition/afc-challenge-league-2945', '/en/competition/egyptian-super-cup-2860', '/en/competition/scottish-league-two-playoffs-2794', '/en/competition/bundesliga-1', 
                   '/en/competition/premier-soccer-league-118', '/en/competition/womens-fa-cup-2757', '/en/competition/caf-champions-league-210', '/en/competition/liga-super-malaysia-147', '/en/competition/austrian-bundesliga-26', 
                   '/en/competition/uae-presidents-cup-2923', '/en/competition/superliga-123', '/en/competition/eerste-divisie-101', '/en/competition/dfb-pokal-4', '/en/competition/superettan-181', '/en/competition/vbet-ukrainian-premier-league-61',
                   '/en/competition/kings-league-mena-2987', '/en/competition/swf-scottish-cup-2940', '/en/competition/copa-fares-lopes-1891', '/en/competition/kings-world-cup-nations-2959', '/en/competition/ligapro-serie-a-172',
                   '/en/competition/eredivisie-36', '/en/competition/uefa-champions-league-5', '/en/competition/major-league-soccer-15', '/en/competition/regionalliga-nord-44', '/en/competition/liga-portugal-35', 
                   '/en/competition/algeria-ligue-2-2957', '/en/competition/regionalliga-bayern-52', '/en/competition/magyar-kupa-2868', '/en/competition/kings-league-germany-2968', '/en/competition/usl-championship-2750',
                   '/en/competition/taca-da-liga-2697', '/en/competition/uefa-womens-champions-league-2702', '/en/competition/fifa-u17-world-cup-188', '/en/competition/conmebol-libertadores-76', '/en/competition/superligaen-57', 
                   '/en/competition/copa-colombia-168', '/en/competition/eliteserien-relegation-play-offs-2910', '/en/competition/premier-league-summer-series-2894', '/en/competition/coppa-italia-serie-c-145', '/en/competition/uefa-conference-league-2762', 
                   '/en/competition/super-league-25', '/en/competition/superliga-colombiana-2752', '/en/competition/knvb-beker-vrouwen-2942', '/en/competition/canadian-premier-league-2705', '/en/competition/primera-division-apertura-179', 
                   '/en/competition/uefa-youth-league-189', '/en/competition/liga-portugal-2-142', '/en/competition/3-lig-2847', '/en/competition/campeonato-paulista-feminino-1909', '/en/competition/liga-f-2704', '/en/competition/russian-premier-league-14', 
                   '/en/competition/liga-premier-219', '/en/competition/afc-womens-champions-league-2953', '/en/competition/3-liga-3', '/en/competition/liga-profesional-argentina-clausura-183', '/en/competition/club-friendlies-women-2800', 
                   '/en/competition/championnat-national-3-1723', '/en/competition/copa-santa-catarina-1894', '/en/competition/serie-d-2741', '/en/competition/toppserien-2813', '/en/competition/caf-womens-champions-league-2943', '/en/competition/hybrid-friendlies-women-2932',
                   '/en/competition/laliga-10', '/en/competition/campionato-primavera-1-timvision-2804', '/en/competition/1-hnl-120', '/en/competition/efl-trophy-143', '/en/competition/the-icon-league-2947', '/en/competition/nifl-premiership-2768', 
                   '/en/competition/super-league-indonesia-148', '/en/competition/concacaf-central-american-cup-2975', '/en/competition/1-divisjon-promotion-playoff-2956', '/en/competition/primera-b-170', '/en/competition/i-league-187', 
                   '/en/competition/bulgarian-cup-2849', '/en/competition/maltese-premier-league-2877', '/en/competition/scottish-challenge-cup-2836', '/en/competition/singapore-premier-league-2883', '/en/competition/ligat-haal-2731', 
                   '/en/competition/conmebol-womens-nations-league-2990', '/en/competition/carioca-2-1886', '/en/competition/persian-gulf-pro-league-2690', '/en/competition/vysheyshaya-liga-2688', '/en/competition/challenger-pro-league-2788',
                   '/en/competition/kazakhstan-premier-league-2766', '/en/competition/serie-a-women-2721', '/en/competition/gvia-hamedina-2872', '/en/competition/a-lyga-2748', '/en/competition/primera-division-de-el-salvador-2726', 
                   '/en/competition/jleague-cup-2875', '/en/competition/slovak-cup-2884', '/en/competition/singapore-cup-2882', '/en/competition/nwsl-challenge-cup-2751', '/en/competition/k-league-promotion-playoff-2735', '/en/competition/friendlies-women-2734',
                   '/en/competition/liga-portugal-3-2767', '/en/competition/superleague-2-2865', '/en/competition/1-snl-2728', '/en/competition/primera-division-clausura-180', '/en/competition/premier-league-2-208', '/en/competition/ettan-2887', 
                   '/en/competition/primera-federacion-rfef-150', '/en/competition/serie-c-144', '/en/competition/indian-super-league-154', '/en/competition/hong-kong-premier-league-2867', '/en/competition/scottish-cup-40', 
                   '/en/competition/womens-super-league-2-2897', '/en/competition/thai-fa-cup-2920', '/en/competition/qatar-fa-cup-2926', '/en/competition/saudi-pro-league-111', '/en/competition/afc-champions-league-two-2760', 
                   '/en/competition/fa-womens-league-cup-2898', '/en/competition/serie-a-13', '/en/competition/regionalliga-west-46', '/en/competition/hong-kong-fa-cup-2866', '/en/competition/premier-division-play-off-2906', 
                   '/en/competition/primera-a-clausura-110', '/en/competition/k-league-1-130', '/en/competition/kings-cup-mexico-2960', '/en/competition/first-professional-football-league-2758', '/en/competition/nwsl-2700', '/en/competition/campeonato-de-portugal-2698', 
                   '/en/competition/premier-league-9', '/en/competition/efl-cup-41', '/en/competition/efl-league-one-42', '/en/competition/ligue-1-tunisia-2687', '/en/competition/armenian-premier-league-2770', '/en/competition/scottish-league-cup-2712',
                   '/en/competition/greek-cup-126', '/en/competition/vleague-1-2890', '/en/competition/torneo-apertura-177', '/en/competition/kings-world-cup-clubs-2969', '/en/competition/liga-2-indonesia-2779', '/en/competition/egyptian-premier-league-2732',
                   '/en/competition/championnat-national-1721', '/en/competition/hybrid-friendlies-2805', '/en/competition/ligue-professionnelle-1-2754', '/en/competition/tweede-divisie-2839', '/en/competition/besta-deild-karla-2689', '/en/competition/uefa-womens-nations-league-2819',
                   '/en/competition/conmebol-libertadores-u20-2886', '/en/competition/scottish-league-two-100', '/en/competition/superliga-romaniei-60', '/en/competition/kategoria-superiore-134', '/en/competition/serbian-cup-2880', '/en/competition/allsvenskan-62', 
                   '/en/competition/kings-league-spain-2904', '/en/competition/allsvenskan-relegation-play-off-2909', '/en/competition/scottish-championship-playoffs-2792', '/en/competition/swpl-1-relegation-play-offs-2914', '/en/competition/veikkausliiga-play-offs-2905', 
                   '/en/competition/eliteserien-67', '/en/competition/cfa-cup-129', '/en/competition/veikkausliiga-680', '/en/competition/azerbaijan-premier-league-2771', '/en/competition/czech-cup-2857', '/en/competition/brasileirao-betano-16', 
                   '/en/competition/a-league-men-84', '/en/competition/premier-division-191', '/en/competition/ukrainian-cup-2981', '/en/competition/estonian-cup-2861', '/en/competition/tonybet-virsliga-2746', '/en/competition/first-league-127', '/en/competition/uae-pro-league-157',
                   '/en/competition/2-liga-116', '/en/competition/cypriot-first-division-2854', '/en/competition/damallsvenskan-2701', '/en/competition/peru-liga-1-176', '/en/competition/copa-de-la-reina-2742', '/en/competition/serie-bkt-30', 
                    '/en/competition/pernambucano-2-1911', '/en/competition/brasileirao-serie-c-195', '/en/competition/northern-super-league-2966', '/en/competition/honduras-liga-nacional-2724', '/en/competition/liga-de-expansion-mx-203', '/en/competition/brasileirao-serie-b-superbet-119',
                    '/en/competition/piala-fa-2833', 
                    '/en/competition/scottish-premiership-39', '/en/competition/china-league-one-2851', '/en/competition/oefb-cup-31', '/en/competition/1-lig-121', '/en/competition/kubok-108', '/en/competition/national-league-north-south-2820', '/en/competition/thai-league-1-2903', 
                    '/en/competition/regionalliga-nordost-50', '/en/competition/ligue-2-29', '/en/competition/caf-confederation-cup-2765', '/en/competition/chance-liga-relegation-playoffs-2973', '/en/competition/premiere-ligue-women-2703', '/en/competition/latvijas-kauss-2876', 
                    '/en/competition/primera-division-82', '/en/competition/cymru-premier-2769', '/en/competition/afc-champions-league-elite-155', '/en/competition/challenge-league-207', '/en/competition/scottish-league-one-playoffs-2793', '/en/competition/brasileirao-serie-d-216', 
                    '/en/competition/j-league-world-challenge-2713', '/en/competition/frauen-bundesliga-47', '/en/competition/club-friendly-games-140', '/en/competition/1-division-2859']
    
    def parse(self, response):
        for url in self.leages_urls:
            tables_url = 'https://onefootball.com' + url + '/table'
            yield scrapy.Request(url=tables_url, callback=self.parse_league)

    def parse_league(self, response):
        import json
        table_item = TableItem()
        json_data = response.css('script#__NEXT_DATA__::text').get()
        data = json.loads(json_data)
        containers = data['props']['pageProps']['containers']
        teams = None
        table_item['table'] = []
        for container in containers:
            try:
                teams = container['type']['fullWidth']['component']['contentType']['standings']['rows']
            except Exception as e:
                self.logger.warning(e)
            try:
                title = container['type']['fullWidth']['component']['contentType']['standings'].get('title')
                if title is not None and title == '':
                    group = None
                elif title is not None and title != '':
                    group = title
            except Exception as e:
                group = None
            if teams:

                for row in teams :
                    league = response.css('div.EntityTitle_content__q7h3j p.title-1-bold-druk.EntityTitle_title__sWSgU::text').get()
                    position = row.get('position')
                    team = row.get('teamName')
                    team_logo = row.get('imageObject').get('path')
                    matches_played = row.get('playedMatchesCount')
                    matches_won = row.get('wonMatchesCount')
                    matches_drawn = row.get('drawnMatchesCount')
                    matches_lost = row.get('lostMatchesCount')
                    goals_diff = row.get('goalsDiff')
                    points = row.get('points')
                    position_change = row.get('positionChange')
                    
                    data = {
                        'league': league,
                        'group': group,
                        'position': position,
                        'team': team,
                        'team_logo': team_logo,
                        'matches_played': matches_played,
                        'matches_won': matches_won,
                        'matches_drawn': matches_drawn,
                        'matches_lost': matches_lost,
                        'goals_diff': goals_diff,
                        'points': points,
                        'position_change': position_change
                    }
                    table_item['table'].append(data)
                    table_item['league'] = league
                    yield table_item
            

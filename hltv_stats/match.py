import os
from datetime import datetime, timedelta
from .parser import Parser
from loguru import logger

BASE_URL = "https://www.hltv.org"


class HLTVMatch(Parser):
    def __init__(self, url):
        self.match_url = url
        self.match_id = self.match_url.split('/')[2]
        self.teams_name = None
        self.teams_link = None
        self.analytics_center_link = None
        self.match_maps = None
        self.datetime = None
        self.__get_match_attributes()

    def __get_match_attributes(self):
        soup = self._soup_from_url(BASE_URL + self.match_url)
        get_normed_link = lambda _: "/" + "/".join(_.split('/')[2:4])
        get_team_name = lambda _: _.split('/')[3]
        team1_link = soup.find("div", class_="team1-gradient").find('a')['href']
        team2_link = soup.find("div", class_="team2-gradient").find('a')['href']
        analytics_link = soup.find("a", class_="matchpage-analytics-center-container")['href']
        self.teams_link = (get_normed_link(team1_link), get_normed_link(team2_link))
        self.teams_name = (get_team_name(team1_link), get_team_name(team2_link))
        self.analytics_center_link = BASE_URL + analytics_link
        timestamp = int(soup.find("div", class_="timeAndEvent").find(class_="time")['data-unix'][0:-3])
        self.datetime = str(datetime.fromtimestamp(timestamp) - timedelta(hours=8))

    def parse_analytics_center(self, filename=None):
        soup = self._soup_from_url(self.analytics_center_link)
        output = []
        try:
            insights = self.parse_analytics_summary(soup)
            output.append(insights)
            if filename is not None:
                self._write_to_json(insights, f"{filename}_insights.json")
        except:
            logger.info("Failed __parse_analytics_summary(), parsed match has non-regular data\n")
        try:
            map_stats = self.parse_pick_ban_stats(soup)
            output.append(map_stats)
            if filename is not None:
                self._write_to_json(map_stats, f"{filename}_maps_stats.json")
        except:
            logger.info("Failed __parse_pick_ban_stats(), parsed match has non-regular data\n")
        try:
            players_stats = self.parse_head_to_head(soup)
            output.append(players_stats)
            if filename is not None:
                self._write_to_json(players_stats, f"{filename}_players_stats.json")
        except:
            logger.info("Failed __parse_head_to_head(), parsed match has non-regular data\n")
        return tuple(output)

    def parse_analytics_summary(self, soup=None, filename=None):
        if not soup:
            soup = Parser._soup_from_url(self.analytics_center_link)
        normed = lambda x: list(map(lambda _: _.text.lower().strip(), x))
        # normed(soup.find('div', attrs={"class", "analytics-info fadeUp"}).find_all("div"))
        insights_stats = []
        for i in range(2):
            container = soup.find(class_=f"analytics-insights-container team{i + 1}")
            plus_len = len(container.find_all(class_="fa fa-plus"))
            minus_len = len(container.find_all(class_="fa fa-minus"))
            plus = ['plus'] * plus_len if plus_len > 0 else ['none']
            minus = ['minus'] * minus_len if minus_len > 0 else ['none']
            indicator = plus + minus
            insights = normed(container.find_all(class_="analytics-insights-insight"))
            for j in range(len(insights)):
                row_data = {
                    "team": self.teams_name[i],
                    "indicator": indicator[j],
                    "insight": insights[j],
                    "match_id": self.match_id
                }
                insights_stats.append(row_data)
        if filename is not None:
            self._write_to_json(insights_stats, f"{filename}.json")
        return insights_stats

    def parse_pick_ban_stats(self, soup=None, filename=None):
        if not soup:
            soup = Parser._soup_from_url(self.analytics_center_link)
        map_stats = []
        rows = soup.find(class_="table-container gtSmartphone-only").find("tbody").find_all('tr')
        for ind, row in enumerate(rows):
            if ind % 2 == 0:
                map_name = row.find('div', class_='analytics-map-name').text.lower()
            team_name = self.teams_name[ind % 2]
            pick_percentage = row.find('td', class_='analytics-map-stats-pick-percentage').text
            ban_percentage = row.find('td', class_='analytics-map-stats-ban-percentage').text
            win_percentage = row.find('td', class_='analytics-map-stats-win-percentage').text
            games_played = row.find('td', class_='analytics-map-stats-played').text
            comment = row.find(class_="analytics-map-stats-comment").text
            row_data = {
                "analytics_map_name": map_name,
                "team": team_name,
                "analytics_map_stats_pick_percentage": pick_percentage,
                "analytics_map_stats_ban_percentage": ban_percentage,
                "analytics_map_stats_win_percentage": win_percentage,
                "analytics_map_stats_played": games_played,
                "analytics_map_stats_comment": comment,
                "match_id": self.match_id
            }
            map_stats.append(row_data)
        if filename is not None:
            self._write_to_json(map_stats, f"{filename}.json")
        return map_stats

    def parse_head_to_head(self, soup=None, filename=None):
        if not soup:
            soup = Parser._soup_from_url(self.analytics_center_link)
        players_stats = []
        team_container = soup.find_all(class_="table-container")  # [0] [1] teams=
        for i in range(2):
            nicknames = team_container[i].find_all(class_='player-nickname')
            three_month_stats = team_container[i].find_all(class_='table-3-months')[1:6]
            event_stats = team_container[i].find_all(class_='table-event')[1:6]
            for player in range(5):
                player_data = {
                    "player_team": self.teams_name[i],
                    "player_nickname": nicknames[player].text,
                    "table_3_months": three_month_stats[player].text,
                    "table_event": event_stats[player].text,
                    "match_id": self.match_id
                }
                players_stats.append(player_data)
        if filename is not None:
            self._write_to_json(players_stats, f"{filename}.json")
        return players_stats

    def is_parsed(self) -> bool:
        """Checks if match is already parsed and adds it to matches_config.json if not"""
        try:
            match_dict = Parser()._read_from_json("./configs/matches_config.json")
        except:
            logger.info("""Created ./configs/match_config.json for mapping""")
            os.makedirs(os.path.dirname("./configs/"), exist_ok=True)
            match_dict = {}
        if self.match_id not in match_dict:
            data = list(map(lambda _: _.replace("-", " "), self.teams_name)).copy()
            data.extend([self.datetime, self.match_id, self.match_url])
            match_dict[self.match_id] = data
            Parser()._write_to_json(match_dict, "./configs/matches_config.json")
            return False
        return True
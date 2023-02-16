import os
from datetime import datetime, timedelta
from cuid import cuid
from .parser import Parser
from loguru import logger
BASE_URL = "https://www.hltv.org"


class HLTVTeam(Parser):
    def __init__(self, url):
        self.team_url = url
        self.team_name = url.split("/")[2].lower()
        self.sliced_url = ("/stats/teams" + url).split("/")
        self.team_cuid = self.__get_cuid(self.team_name)
        self.match_id = None

    def __get_cuid(self, team_name):
        """
        Returns unique id for team name. If team name is not in team_config.json, creates new id and writes to file.
        """
        try:
            team_dict = self._read_from_json("./configs/team_config.json")
        except:
            logger.info("""Created ./configs/team_config.json for mapping {"team name" : "unique id"}""")
            os.makedirs(os.path.dirname("./configs/"), exist_ok=True)
            team_dict = {}
        if team_name not in team_dict:
            team_dict[team_name] = cuid()
            self._write_to_json(team_dict, "./configs/team_config.json")
        return team_dict[team_name]

    @staticmethod
    def __get_time_filter(months=0):
        """ Returns time filter for url"""
        if months == 0:
            return '?startDate=all'
        date = datetime.now()
        start_date = datetime.strftime(date - timedelta(days=int(30 * months)), '%Y-%m-%d')
        end_date = datetime.strftime(date, '%Y-%m-%d')
        return f'?startDate={start_date}&endDate={end_date}'

    def parse_all_stats(self, time_filter: int, filename: str = None):
        """ Parse all stats for team
        :param time_filter: 0 - all time, 1 - last month, 2 - last 2 months, 3 - last 3 months
        :param filename: str, filename for saving json
        :return: tuple of list of dicts with stats
        """
        output = []
        try:
            matches_stats = self.parse_matches(time_filter)
            output.append(matches_stats)
            if filename is not None:
                self._write_to_json(matches_stats, f"{filename}_matches_stats.json")
        except:
            logger.info("Failed parse_matches()")
        try:
            maps_stats = self.parse_maps(time_filter)
            output.append(maps_stats)
            if filename is not None:
                self._write_to_json(maps_stats, f"{filename}_maps_stats.json")
        except:
            logger.info("Failed parse_maps()")
        try:
            players_stats = self.parse_players(time_filter)
            output.append(players_stats)
            if filename is not None:
                self._write_to_json(players_stats, f"{filename}_players_stats.json")
        except:
            logger.info("Failed parse_players()")
        try:
            events_stats = self.parse_events(time_filter)
            output.append(events_stats)
            if filename is not None:
                self._write_to_json(events_stats, f"{filename}_events_stats.json")
        except:
            logger.info("Failed parse_events()")
        return tuple(output)

    def parse_matches(self, time_filter=3, filename=None):
        """
        Parse played matches stats for team;
        :param time_filter: int, 0 = all time, 1 - 1 month, 6 - 6 months, ...
        :param filename: str, filename to save json
        :return: list of dicts with matches stats
        """

        matches_url = "/".join(self.sliced_url[0:3]) + "/matches/" + "/".join(self.sliced_url[3:5])
        start_url = BASE_URL + matches_url + self.__get_time_filter(time_filter)
        soup = self._soup_from_url(start_url)

        matches_stats = []
        rows = soup.find_all('tr', attrs={"class": "group-1 first"}) + \
               soup.find_all('tr', attrs={"class": "group-2 first"}) + \
               soup.find_all('tr', attrs={"class": "group-1"}) + \
               soup.find_all('tr', attrs={"class": "group-2"})
        for row in rows:
            row_elements = row.find_all("td")

            row_date = row_elements[0].a
            row_event = row_elements[1].span
            row_opponent = row_elements[3].a
            row_map = row_elements[4].span
            row_result = row_elements[5].span
            row_flag = row_elements[6]
            norm = lambda _: _.text.lower()
            row_data = {
                "team": self.team_name,
                "date": norm(row_date),
                "event": norm(row_event),
                "opponent": norm(row_opponent).strip().replace(" ", "-"),
                "map": norm(row_map),
                "result": norm(row_result),
                "flag": row_flag.text,
                "team_cuid": self.team_cuid,
                "time_filter": str(time_filter)
            }
            if self.match_id is not None:
                row_data['match_cuid'] = self.match_id
            matches_stats.append(row_data)
        if filename is not None:
            self._write_to_json(matches_stats, f"{filename}.json")
        return matches_stats

    def parse_maps(self, time_filter=3, filename=None):
        """
        Parse played maps stats for team;
        :param time_filter: int, 0 - all time, 1 - 1 month, 6 - 6 months, ...
        :param filename: str, filename to save json
        :return: list of dicts with maps stats
        """

        maps_url = "/".join(self.sliced_url[0:3]) + "/maps/" + "/".join(self.sliced_url[3:5])
        start_url = BASE_URL + maps_url + self.__get_time_filter(time_filter)
        soup = self._soup_from_url(start_url)

        maps_stats = []
        map_names = soup.find_all("div", attrs={'class': 'map-pool-map-name'})
        map_stats = soup.find_all("div", attrs={'class': 'stats-rows standard-box'})

        for i in range(len(map_stats)):
            map_name = map_names[i]
            stats = list(map(lambda _: _.find_all('span')[1].text, map_stats[i].find_all('div')))
            map_data = {
                "team": self.team_name,
                "map": map_name.text.split("-")[0].rstrip().lower(),
                "wins_draws_losses": stats[0],
                "win_rate": stats[1],
                "total_rounds": stats[2],
                "round_win_perc_after_first_kill": stats[3],
                "round_win_perc_after_first_death": stats[4],
                "team_cuid": self.team_cuid,
                "time_filter": str(time_filter)
            }
            if self.match_id is not None:
                map_data['match_cuid'] = self.match_id
            maps_stats.append(map_data)
        if filename is not None:
            self._write_to_json(maps_stats, f"{filename}.json")
        return maps_stats

    def parse_players(self, time_filter=3, filename=None):
        """
        Parse players stats for team;
        :param time_filter: int, 0 - all times, 1 - 1 months, 6 - 6 months, ...
        :param filename: str, filename to save json
        :return: list of dicts with players stats
        """

        players_url = "/".join(self.sliced_url[0:3]) + "/players/" + "/".join(self.sliced_url[3:5])
        start_url = BASE_URL + players_url + self.__get_time_filter(time_filter)
        soup = self._soup_from_url(start_url)
        players_stats = []
        players = soup.find_all("tr")
        for i in range(1, 10):
            try:
                player = list(map(lambda _: _.text, players[i].find_all('td')))
                player_data = {
                    "team": self.team_name,
                    "player": player[0],
                    "maps": player[1],
                    "rounds": player[2],
                    "kd_diff": player[3],
                    "kd": player[4],
                    "rating": player[5],
                    "team_cuid": self.team_cuid,
                    "time_filter": str(time_filter)
                }
                if self.match_id is not None:
                    player_data['match_cuid'] = self.match_id
                players_stats.append(player_data)
            except:
                pass
        if filename is not None:
            self._write_to_json(players_stats, f"{filename}.json")
        return players_stats

    def parse_events(self, time_filter=3, filename=None):
        """Parse events stats for team
        :param time_filter: int, 0 - all times, 1 - 1 months, 6 - 6 months, ...
        :param filename: str, filename to save json
        :return: list of dicts with events stats
        """
        events_url = "/".join(self.sliced_url[0:3]) + "/events/" + "/".join(self.sliced_url[3:5])
        start_url = BASE_URL + events_url + self.__get_time_filter(time_filter)
        soup = self._soup_from_url(start_url)

        events_stats = []
        events = soup.find_all("tr")
        for i in range(1, len(events)):
            event = list(map(lambda _: _.text.lower(), events[i].find_all('td')))
            event_data = {
                "placement": event[0],
                "event": event[1],
                "team": self.team_name,
                "team_cuid": self.team_cuid,
                "time_filter": str(time_filter)
            }
            if self.match_id is not None:
                event_data['match_cuid'] = self.match_id
            events_stats.append(event_data)

        if filename is not None:
            self._write_to_json(events_stats, f"{filename}.json")
        return events_stats
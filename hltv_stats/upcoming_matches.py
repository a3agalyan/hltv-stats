import os
from hltv_stats_parser import Parser, HLTVMatch, HLTVTeam
BASE_URL = "https://www.hltv.org"


def get_links_upcoming_matches(include_live=True):
    """Get links to random number of live and upcoming(!!!) matches
    :param include_live: bool, include live matches
    """
    matches_page_url = "https://www.hltv.org/matches"
    soup = Parser._soup_from_url(url=matches_page_url)
    matches = soup.find("div", class_="upcomingMatchesSection") \
        .find_all('a', class_="match a-reset", href=True)
    links = []
    for match in matches:
        team_count = match.parent.find_all('div', class_="matchTeamName text-ellipsis")
        if len(team_count) < 2:
            print(match['href'])
            print("Invalid match, waiting for teams")
        else:
            links.append(match['href'])
    if include_live:
        lives = soup.find_all("div", class_="liveMatch")
        lives = list(map(lambda _: _.a['href'], lives))
        links.extend(lives)
    return links


def parse_upcoming_matches(months, with_teams=False):
    """Parse upcoming matches and save to json files
    :param months: list of months to parse, i.e. [1,3] <=> [last month, last 3 months]
    :param with_teams: bool, if True, parse teams' statistic as well
    :param write_to_file: bool, if True, creates tree of folders and saves json files like output/matches/
    """
    dir_path = os.path.join(os.getcwd(), "output/")
    matches_path = dir_path + "matches/"
    teams_path = dir_path + "teams/"
    os.makedirs(os.path.dirname(matches_path), exist_ok=True)
    os.makedirs(os.path.dirname(teams_path), exist_ok=True)
    matches_link = get_links_upcoming_matches()
    for ind, match_link in enumerate(matches_link):
        print("parsing :", match_link)
        try:
            match = HLTVMatch(BASE_URL + match_link)
            if match.is_parsed():
                print("Match already parsed, skipping")
                continue
            match.parse_analytics_center(filename=f"{matches_path}/{match.match_id}")
            teams = match.teams_link
            if with_teams:
                for m in months:
                    team1 = HLTVTeam(teams[0])
                    team1.match_id = match.match_id
                    team1.parse_all_stats(time_filter=m,
                                          filename=f"{teams_path}/{match.match_id}_{team1.team_name.replace('-', '_')}")
                    team2 = HLTVTeam(teams[1])
                    team2.match_id = match.match_id
                    team2.parse_all_stats(time_filter=m,
                                          filename=f"{teams_path}/{match.match_id}_{team2.team_name.replace('-', '_')}")
        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e))
            print("""Invalid match, probably empty stats""")


if __name__ == '__main__':
    parse_upcoming_matches(months=[3], with_teams=True)
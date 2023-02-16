<p>
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.6-blue.svg?cacheSeconds=2592000" />
  <a href="#" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
</p>

> Hi, I analyze hltv.org as a part of my pet project.
> This parser can help you build a prematch analytics dataset with data from [Team stats]( https://www.hltv.org/stats/teams) and [Analytics](https://www.hltv.org/betting/analytics) pages.



## Install

```sh
pip install hltv-stats
```

## Usage
#### ```HLTVMatch``` provides public methods for [Analytics](https://www.hltv.org/betting/analytics), use ```filename``` parameter to save data to a file.
```sh
from hltv_stats import HLTVMatch
match_url = "/matches/2361342/natus-vincere-vs-outsiders-iem-katowice-2023"
match = HLTVMatch(match_url)
```
```sh
match.parse_analytics_summary(filename=None)
```

```sh
Response:

[{'team': 'natus-vincere',
  'indicator': 'plus',
  'insight': 'natus vincere has better form ranking',
  'match_id': '2361342'},
    ...
]
```
```sh
match.parse_head_to_head()
```

```sh
Response:

[{'player_team': 'natus-vincere',
  'player_nickname': 's1mple',
  'table_3_months': '1.13',
  'table_event': '1.17',
  'match_id': '2361342'},
    ...
]
```
```sh
match.parse_pick_ban_stats()
```

```sh
Response:

[{'analytics_map_name': 'mirage',
  'team': 'natus-vincere',
  'analytics_map_stats_pick_percentage': '39%',
  'analytics_map_stats_ban_percentage': '0%',
  'analytics_map_stats_win_percentage': '29%',
  'analytics_map_stats_played': '7',
  'analytics_map_stats_comment': 'First pick',
  'match_id': '2361342'},
    ...
]
```
```match.parse_analytics_center()``` method combines all above methods and returns a tuple of lists.

#### ```HLTVTeam``` provides public methods for parsing [Team stats page]( https://www.hltv.org/stats/teams), with filtering by time using ```time_filter``` parameter, use ```filename``` parameter to save data to a file.
```sh
from hltv_stats import HLTVTeam
team = HLTVTeam("/4608/natus-vincere")
#You can use match_id to assign team's current state(statistic) to specific match
#this will add match_id field to all json files
team.match_id = match.match_id
```
```sh
#time_filter: 3 - last 3 months, 6 - last 6 months, 0 - all time, ...
team.parse_matches(time_filter=1) #returns list of played matches in json format
team.parse_players(time_filter=1) #returns list of team players' statistics in json format
team.parse_maps(time_filter=1) #returns maps statistics in json format
team.parse_events(time_filter=1) #returns events statistics in json format

team.parse_all_stats(time_filter=1)
```
```.parse_all_stats(time_filter=1)``` method combines all above methods and returns a tuple of lists.

#### ```parse_upcoming_matches()``` method parses all upcoming matches from [Match page](https://www.hltv.org/matches).
```sh
#Parse upcoming matches and save to json files
#:param months: list of months to parse, i.e. [1,3] <=> [last month, last 3 months]
#:param with_teams: bool, if True, parse teams' statistic as well

from hltv_stats import parse_upcoming_matches
parse_upcoming_matches(months=[1], with_teams=True)
```


```
Result folder tree contains json files with all match data, and team data if with_teams=True.
.
├── configs - contains 2 config files: which holds data about all parsed matches and teams and are used by is_parsed() method to check if match is already parsed and skips it.
├── output
│   ├── matches 
│   └── teams
```
#### Also check out example.ipynb or contact me.

### 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/a3agalyan/hltv-stats/issues). 

### Show your support

Give a ⭐️ if this project helped you!
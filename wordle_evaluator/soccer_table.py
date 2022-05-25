from dataclasses import dataclass
from datetime import datetime
from scoreboard import Scoreboard
import pandas as pd

from scorereader import (
    get_days_played_from_scores,
    get_players_from_scores,
)


@dataclass
class SoccerTable:
    scoreboard: Scoreboard

    def get_table(self, month: int, year: int) -> pd.DataFrame:
        scores = self.scoreboard.get_all_scores()
        relevant_scores = [
            score
            for score in scores
            if year == score.date.year and month == score.date.month
        ]
        relevant_days = sorted(get_days_played_from_scores(relevant_scores))
        players = get_players_from_scores(relevant_scores)
        print(players)
        table_dict = dict(
            Player=[player.name for player in players],
            Wins=[0] * len(players),
            Ties=[0] * len(players),
            Boobies=[0] * len(players),
            Points=[0] * len(players),
        )
        for day in relevant_days:
            print(day)
            winners = self.scoreboard.get_winners_of_day(day=day)
            print(winners)
            p_ids = [table_dict["Player"].index(w) for w in winners]
            if len(winners) == 1:
                for i in range(len(players)):
                    if i in p_ids:
                        table_dict["Wins"][i] += 1
                        table_dict["Points"][i] += 3
                    else:
                        table_dict["Boobies"][i] += 1
            elif len(winners) > 1:
                for i in range(len(players)):
                    if i in p_ids:
                        table_dict["Ties"][i] += 1
                        table_dict["Points"][i] += 1
                    else:
                        table_dict["Boobies"][i] += 1
        table = pd.DataFrame(table_dict)

        table.set_index("Player", inplace=True)
        table.sort_values(by="Points", inplace=True, ascending=False)
        return table

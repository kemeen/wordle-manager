from dataclasses import dataclass
from typing import List
from scoreboard import Scoreboard
import pandas as pd

from scorereader import (
    filter_scores_by_game_ids,
    filter_scores_by_provider,
    get_days_played_from_scores,
    get_players_from_scores,
)
from provider import Provider


@dataclass
class SoccerTable:
    scoreboard: Scoreboard

    def get_table_by_date(self, month: int, year: int) -> pd.DataFrame:
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
            # print(day)
            winners = self.scoreboard.get_winners_of_day(day=day)
            # print(winners)
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

    def get_table_by_game_ids(
        self, games: dict[str, List[int]], providers: List[Provider]
    ) -> pd.DataFrame:
        provider_names = list(games.keys())
        game_ids = zip(*games.values())
        players = list(self.scoreboard.players)

        table_dict = dict(
            Player=[player.name for player in players],
            Wins=[0] * len(players),
            Ties=[0] * len(players),
            Boobies=[0] * len(players),
            Points=[0] * len(players),
        )

        for day_game_ids in game_ids:
            print(day_game_ids)
            scores = []
            for provider_name, game_id in zip(provider_names, day_game_ids):
                # print(provider_name)
                provider = [p for p in providers if p.name == provider_name][0]
                provider_scores = filter_scores_by_provider(
                    scores=self.scoreboard.get_all_scores(),
                    provider=provider,
                )
                scores.extend(
                    filter_scores_by_game_ids(
                        scores=provider_scores, game_ids=[game_id]
                    )
                )

            if len(scores) == 0:
                continue

            winners = self.scoreboard.get_winners_from_scores(scores=scores)
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
            # break
        table = pd.DataFrame(table_dict)

        table.set_index("Player", inplace=True)
        table.sort_values(by="Points", inplace=True, ascending=False)
        return table

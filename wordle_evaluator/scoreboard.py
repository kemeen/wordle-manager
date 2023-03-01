from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Set, Tuple
import pandas as pd
import numpy as np

from .player import Player
from .provider import Provider
from .scorereader import (
    Score,
    filter_scores_by_date,
    filter_scores_by_player,
    filter_scores_by_provider,
    get_days_played_from_scores,
    get_players_from_scores,
    get_providers_from_scores,
)

MAX_POINTS = 7


@dataclass
class Scoreboard:
    # score_readers: Dict[Provider, ScoreReader] = field(default_factory=dict)
    scores: List[Score] = field(default_factory=list)
    players: Set[Player] = field(default_factory=set)

    def register_reader(self, provider, reader) -> None:
        self.score_readers[provider] = reader

    def register_scores(self, scores: List[Score]) -> None:
        for score in scores:
            if score in self.scores:
                # print(f"Score already registered: {str(score)}")
                continue
            self.scores.append(score)

    def update_players_from_scores(self) -> None:
        scores = self.get_all_scores()
        self.players = self.players.union(get_players_from_scores(scores=scores))

    def register_players(self, players: List[Player]) -> None:
        self.players = self.players.union(players)

    def get_all_scores(self) -> List[Score]:
        return sorted(self.scores, key=lambda x: x.date)

    def get_scores_as_dataframe(self) -> pd.DataFrame:
        data_dict = {
            "player": [score.player.name for score in self.scores],
            "points": [score.points for score in self.scores],
            "date": [score.date.date() for score in self.scores],
            "time": [score.date.time() for score in self.scores],
            "provider": [score.provider.name for score in self.scores],
            "game_id": [score.game_id for score in self.scores],
        }
        return pd.DataFrame(data=data_dict)

    def get_scores_for_provider(self, provider: Provider) -> List[Score]:
        return filter_scores_by_provider(scores=self.scores, provider=provider)

    def get_players_for_day(self, date: date) -> Set[Player]:
        scores = self.get_all_scores()
        day_scores = filter_scores_by_date(scores=scores, date=date)
        return set([score.player for score in day_scores])

    def get_player_points_of_day(self, date: date) -> pd.DataFrame:
        # get players for the day
        players = sorted(self.get_players_for_day(date), key=lambda player: player.name)

        results = {"players": [player.name for player in players]}

        for provider in get_providers_from_scores(scores=self.scores):
            results[provider.name] = [MAX_POINTS] * len(players)
            provider_scores = filter_scores_by_provider(
                scores=self.scores, provider=provider
            )
            day_scores = filter_scores_by_date(scores=provider_scores, date=date)

            for i, player in enumerate(players):
                player_scores = filter_scores_by_player(
                    scores=day_scores, player=player
                )
                if not player_scores:
                    continue
                max_score = max(player_scores, key=lambda x: x.points)
                results[provider.name][i] = max_score.points
        # print(results)

        results_df = pd.DataFrame(results)
        results_df.set_index("players", inplace=True)
        results_df["total"] = results_df.sum(axis=1).values
        results_df.sort_values(by="total", inplace=True)
        return results_df

    def get_winners_of_day(self, day: date, provider: Provider) -> List[Player]:

        player_points_of_day = self.get_player_points_of_day(date=day)
        # print(player_points_of_day)
        col = "total"
        if provider:
            col = provider.name
        min_points = player_points_of_day[col].min()
        return player_points_of_day.index[
            player_points_of_day[col] == min_points
        ].tolist()

    def get_winners_from_scores(
        self, scores: List[Score], provider: Provider
    ) -> List[Player]:

        # for score in scores:
        #     print(score)

        player_points = self.get_player_points_from_scores(scores=scores)
        # print(player_points)

        col = "total"
        if provider:
            col = provider.name
        min_points = player_points[col].min()
        return player_points.index[player_points[col] == min_points].tolist()

    def get_loosers_of_day(self, day: datetime) -> List[Player]:
        player_points_of_day = self.get_player_points_of_day(date=day)
        return player_points_of_day.idxmax()["total"]

    def is_day_complete(self, date: date) -> bool:
        scores = self.get_all_scores()
        scores = filter_scores_by_date(scores=scores, date=date)
        providers = get_providers_from_scores(scores=scores)

        for player in self.players:
            players_scores = filter_scores_by_player(scores=scores, player=player)
            player_providers = get_providers_from_scores(scores=players_scores)
            if not providers == player_providers:
                return False
        return True

    def get_wins_per_player(self) -> Dict[Player, int]:
        scores = self.get_all_scores()
        days = list(get_days_played_from_scores(scores))

        results = dict()
        for day in sorted(days):
            if not self.is_day_complete(day):
                continue
            winners = self.get_winners_of_day(day=day)
            for player in winners:
                if not player in results:
                    results[player] = 0
                results[player] += 1

        return {k: v for k, v in sorted(results.items(), key=lambda item: item[1])}

    def get_boobies_per_player(self) -> Dict[Player, int]:
        scores = self.get_all_scores()
        days = list(get_days_played_from_scores(scores))

        results = dict()
        for day in sorted(days):
            if not self.is_day_complete(day):
                continue
            boobies = self.get_loosers_of_day(day=day)
            for player in boobies:
                if not player in results:
                    results[player] = 0
                results[player] += 1

        return {k: v for k, v in sorted(results.items(), key=lambda item: item[1])}

    def get_provider(self, name: str) -> Provider:
        for provider in self.score_readers:
            if provider.name == name:
                return provider

    def get_longest_win_streak(self, provider: Provider) -> List[Score]:
        scores = self.get_all_scores()

        if Provider:
            scores = filter_scores_by_provider(scores=scores)
        days = get_days_played_from_scores(scores=scores)

        for day in days:
            self.get_winners_of_day(day=day)
        pass

    def get_moving_average_scores(
        self,
        player: Player,
        day: datetime,
        provider: Provider,
        window: int = 5,
    ) -> Tuple[List[float], List[datetime]]:
        scores = self.get_all_scores()
        if provider:
            scores = filter_scores_by_provider(scores=scores, provider=provider)
        player_scores = filter_scores_by_player(scores=scores, player=player)
        if day:
            player_scores = [
                Score for score in scores if score.date.date() <= day.date()
            ]
        points = [score.points for score in player_scores]
        days = [score.date for score in player_scores]
        average_points = np.convolve(points, np.ones(window) / window, mode="valid")
        return (average_points.tolist(), days[-len(average_points) :])

    def get_player_points_from_scores(self, scores: List[Score]) -> pd.DataFrame:
        # get players for the day
        players = sorted(self.players, key=lambda player: player.name)

        results = {"players": [player.name for player in players]}

        # for score in scores:
        #     print(score)

        for provider in get_providers_from_scores(scores=scores):
            results[provider.name] = [MAX_POINTS] * len(players)
            provider_scores = filter_scores_by_provider(
                scores=scores, provider=provider
            )
            # print(provider_scores)

            for i, player in enumerate(players):
                player_scores = filter_scores_by_player(
                    scores=provider_scores, player=player
                )
                if not player_scores:
                    continue
                max_score = max(player_scores, key=lambda x: x.points)
                # print(player, max_score)
                results[provider.name][i] = max_score.points
        # print(results)

        results_df = pd.DataFrame(results)
        results_df.set_index("players", inplace=True)
        results_df["total"] = results_df.sum(axis=1).values
        results_df.sort_values(by="total", inplace=True)
        return results_df

    def last_score(self) -> date:
        sorted_scores = sorted(self.scores, key=lambda x: x.date)
        return sorted_scores[-1].date

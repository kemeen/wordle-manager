from dataclasses import dataclass
from datetime import datetime
from typing import List, Protocol, Tuple
from matplotlib import dates, ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas

from scoreboard import (
    Scoreboard,
    filter_scores_by_date,
    filter_scores_by_player,
    get_days_played_from_scores,
    get_players_from_scores,
)
from provider import Provider
from player import Player


class WordleUI(Protocol):
    def show(self) -> None:
        ...


@dataclass
class BarChartWordleUI:
    score_board: Scoreboard

    def show(self) -> None:
        with plt.xkcd():
            fig, ax = plt.subplots(figsize=(15, 8))
            # dff = df[df['year'].eq(year)].sort_values(by='value', ascending=True).tail(10)
            # ax.clear()
            # player_wins = self.score_board.get_wins_per_player()
            # players = [player.name for player in player_wins]
            # points = [point for point in player_wins.values()]
            # winner_bars = ax.barh(players, points, align='center', label='Crowns')
            # ax.bar_label(winner_bars)

            player_loses = self.score_board.get_boobies_per_player()
            players = [player.name for player in player_loses]
            points = [point for point in player_loses.values()]
            booby_bars = ax.barh(
                players, points, align="center", label="Boobies", color="r"
            )
            ax.bar_label(booby_bars)

            plt.box(False)
            plt.show()

    def show_total_results_seaborn(self) -> None:
        with plt.xkcd():
            # sns.set_theme(style="xkcd")
            # create dataframe
            player_wins = self.score_board.get_wins_per_player()
            player_loses = self.score_board.get_boobies_per_player()
            data = pandas.DataFrame(columns=["Name", "Crowns", "Boobies"])
            players = list(player_loses.keys())
            data.Name = [player.name for player in players]
            data.Crowns = [player_wins[player] for player in players]
            data.Boobies = [player_loses[player] for player in players]
            # print(data)
            ax = sns.catplot(x="", data=data, orient="h")
            plt.show()


class CLIWordleUI:
    score_board: Scoreboard

    def show_total_results(self) -> None:
        data = self.score_board.get_wins_per_player()
        print("Total Wordle results")
        for player, wins in data.items():
            print(f"{player.name} won {wins} times")


@dataclass
class MatPlotLibUI:
    score_board: Scoreboard

    def show_total_results(self) -> None:
        pass

    def show_results_over_time(
        self,
        title: str,
        provider: Provider | None = None,
        to_file: bool = False,
    ) -> None:
        if provider is None:
            scores = self.score_board.get_all_scores()
        else:
            scores = self.score_board.get_scores_for_provider(provider=provider)

        # get players
        players = sorted(list(self.score_board.players), key=lambda player: player.name)
        days = sorted(list(get_days_played_from_scores(scores)))

        player_histories = [[] for _ in players]
        current_wins = [0] * len(players)
        for _, day in enumerate(days):

            day_winners = self.score_board.get_winners_of_day(
                day=day, provider=provider
            )
            for i, player in enumerate(players):
                if player.name in day_winners:
                    current_wins[i] += 1

            for k, value in enumerate(current_wins):
                player_histories[k].append(value)
        # print(current_wins)
        # print(len(days))
        # for player_history in player_histories:
        #     print(len(player_history))
        #     print(player_history)

        with plt.xkcd():
            fig, ax = plt.subplots()

            day_locator = dates.DayLocator(interval=7)
            date_formatter = dates.DateFormatter("%d-%m")

            ax.xaxis.set_major_locator(day_locator)
            ax.xaxis.set_major_formatter(date_formatter)

            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

            ax.set_title(title)

            for player, player_history in zip(players, player_histories):
                ax.plot(days, player_history, label=player.name, color=player.color)

            fig.autofmt_xdate()

            plt.legend()
            plt.tight_layout()

            if to_file:
                fig.savefig(f"{title}.png")
                return

            plt.show()

    def plot_moving_average(
        self,
        title: str,
        day: datetime | None = None,
        window_size: int = 5,
        provider: Provider | None = None,
        to_file: bool = False,
    ) -> None:

        if provider:
            provider = self.score_board.get_provider(provider)

        with plt.xkcd():
            fig, ax = plt.subplots()
            fig.set_size_inches(16, 10)

            day_locator = dates.DayLocator(interval=7)
            date_formatter = dates.DateFormatter("%d-%m")

            ax.xaxis.set_major_locator(day_locator)
            ax.xaxis.set_major_formatter(date_formatter)

            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

            ax.set_title(title)

            for player in self.score_board.players:
                values, days = self.score_board.get_moving_average_scores(
                    player=player, provider=provider, window=window_size
                )
                ax.plot(days, values, label=player.name, color=player.color)

            fig.autofmt_xdate()

            plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
            plt.tight_layout()

            if to_file:
                fig.savefig(f"{title}.png")
                return

            plt.show()


@dataclass
class PlayerTimeHistoryPlot:
    data: List[Tuple[Player, List[datetime], List[float | int]]]
    title: str
    to_file: bool = (False,)

    def show(self) -> None:

        with plt.xkcd():
            fig, ax = plt.subplots()
            fig.set_size_inches(8, 5)

            day_locator = dates.DayLocator(interval=7)
            date_formatter = dates.DateFormatter("%d-%m")

            ax.xaxis.set_major_locator(day_locator)
            ax.xaxis.set_major_formatter(date_formatter)

            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

            ax.set_title(self.title)

            for player, days, values in self.data:
                ax.plot(days, values, label=player.name, color=player.color)

            fig.autofmt_xdate()

            plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
            plt.tight_layout()

            if self.to_file:
                fig.savefig(f"{self.title}.png")
                return

            plt.show()
